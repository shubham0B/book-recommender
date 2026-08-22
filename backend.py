import os
import concurrent.futures
import re
import json
import time
import base64
import httpx
import requests
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Set
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client
import google.generativeai as genai

from ingestion import (
    books_collection,
    get_embedding_model,
    get_or_create_query_embedding,
    ingestion_service,
    classify_book_genres,
    make_dedup_key,
    build_semantic_text,
    normalize_string,
    resolve_authentic_cover,
    is_famous_author,
    is_bestseller_title,
    GENRE_MAP,
    RELEVANCE_THRESHOLD,
    MIN_QUALITY_CANDIDATES,
    GOOGLE_BOOKS_MAX_RESULTS,
    SIMILAR_THRESHOLD,
    SIMILAR_MIN_QUALITY,
    ensure_database_loaded
)

load_dotenv()

def is_valid_cover_url(url: str) -> bool:
    if not url or not url.startswith("http") or "/placeholder.svg" in url or "cover-not-found" in url:
        return False
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, stream=True, timeout=1.2)
        if r.status_code != 200:
            return False
        content_type = r.headers.get("Content-Type", "")
        if "image" not in content_type:
            return False
        content_length = r.headers.get("Content-Length")
        if content_length and int(content_length) < 1000:
            return False
        chunk = next(r.iter_content(chunk_size=1024), b"")
        if len(chunk) < 100:
            return False
        return True
    except Exception:
        return False

def filter_books_with_valid_covers(books: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
    valid_books = []
    # Submit with original index to maintain similarity ranking
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=60)
    future_to_book = {
        executor.submit(is_valid_cover_url, b.get("thumbnail", "")): (i, b)
        for i, b in enumerate(books)
    }
    
    for future in concurrent.futures.as_completed(future_to_book):
        i, book = future_to_book[future]
        if future.result():
            valid_books.append((i, book))
            if len(valid_books) >= limit:
                break
                
    # Terminate remaining futures instantly without blocking
    executor.shutdown(wait=False, cancel_futures=True)
    
    # Sort the collected valid books by their original index to restore exact ranking
    valid_books.sort(key=lambda x: x[0])
    return [b for i, b in valid_books]

app = FastAPI(title="BookMind Dynamic Semantic Recommendation API")

@app.on_event("startup")
def startup_db_check():
    count = ensure_database_loaded()
    print(f"[Backend Startup] Verified database loaded with {count} books.")

@app.get("/health")
def health():
    import ingestion
    count = ensure_database_loaded()
    return {
        "status": "healthy",
        "books_count": count,
        "sqlite_exists": os.path.exists(ingestion.SQLITE_PATH),
        "zip_exists": os.path.exists(ingestion.ZIP_PATH)
    }

@app.get("/debug_db")
def debug_db():
    import sqlite3, ingestion
    info = {}
    info["chroma_dir"] = ingestion.CHROMA_DIR
    info["chroma_dir_exists"] = os.path.exists(ingestion.CHROMA_DIR)
    info["chroma_dir_files"] = os.listdir(ingestion.CHROMA_DIR) if os.path.exists(ingestion.CHROMA_DIR) else []
    info["sqlite_path"] = ingestion.SQLITE_PATH
    info["sqlite_exists"] = os.path.exists(ingestion.SQLITE_PATH)
    if os.path.exists(ingestion.SQLITE_PATH):
        info["sqlite_size"] = os.path.getsize(ingestion.SQLITE_PATH)
        try:
            conn = sqlite3.connect(ingestion.SQLITE_PATH)
            cur = conn.cursor()
            info["collections"] = cur.execute("SELECT id, name FROM collections").fetchall()
            info["embeddings_count"] = cur.execute("SELECT count(*) FROM embeddings").fetchone()[0]
            conn.close()
        except Exception as e:
            info["sqlite_error"] = str(e)
    try:
        info["chroma_client_collections"] = [c.name for c in ingestion.chroma_client.list_collections()]
        info["books_collection_count"] = ingestion.books_collection.count()
    except Exception as e:
        info["chroma_error"] = str(e)
    return info

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.exists("frontend"):
    app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key:
    try:
        genai.configure(api_key=gemini_key)
        gemini_model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        print(f"Gemini init warning: {e}")
        gemini_model = None
else:
    gemini_model = None

CURATED_GENRES = [
    "All",
    "Fiction",
    "Nonfiction",
    "Children's Fiction",
    "Children's Nonfiction",
    "Fantasy",
    "Science Fiction",
    "Mystery",
    "Thriller",
    "Horror",
    "Romance",
    "Self Development",
    "Psychology",
    "History",
    "Philosophy",
    "Biography",
    "Young Adult"
]


# ── VECTOR STORE INITIALIZATION ──────────────────────────────────────
try:
    print(f"[Vector Database] ChromaDB collection '{books_collection.name}' initialized. Current count: {books_collection.count()} books.")
except Exception as e:
    print(f"[Vector Database Warning] Error checking ChromaDB count: {e}")



# ── VECTOR SEARCH RETRIEVAL ENGINE ───────────────────────────────────

def vector_search_books(
    query: str = "",
    target_genres: Optional[List[str]] = None,
    limit: int = 48,
    min_similarity: float = RELEVANCE_THRESHOLD,
    allow_dynamic_ingest: bool = True
) -> List[Dict[str, Any]]:
    """
    Perform semantic vector similarity search in ChromaDB.
    Evaluates result quality against dynamic relevance thresholds.
    Only if quality candidate count is insufficient does it query Google Books API,
    embeds ONLY new books, and re-ranks unified results in a single vector search pass.
    """
    active_genres = [g.strip() for g in (target_genres or []) if g and g.strip() != "All"]
    clean_q = (query or "").strip()
    is_general_browse = not clean_q or clean_q.lower() == 'popular'

    # 1. Build Query Text and fetch cached/encoded Embedding Vector
    if is_general_browse:
        if active_genres:
            effective_q = f"Top acclaimed famous books in {' and '.join(active_genres)}"
        else:
            effective_q = "Top acclaimed popular books and classic literature across all genres"
    else:
        if active_genres:
            effective_q = f"{clean_q}. Genre: {', '.join(active_genres)}"
        else:
            effective_q = clean_q

    query_vec = get_or_create_query_embedding(effective_q)

    # 2. Query ChromaDB Vector Store across full collection
    n_fetch = min(max(limit * 8, 800), max(1, books_collection.count()))

    try:
        res = books_collection.query(
            query_embeddings=[query_vec],
            n_results=n_fetch,
            include=["metadatas", "distances"]
        )
    except Exception as e:
        print(f"[Vector Search] Fallback to full semantic query ({e})...")
        res = books_collection.query(
            query_embeddings=[query_vec],
            n_results=n_fetch,
            include=["metadatas", "distances"]
        )

    retrieved_metas = res.get("metadatas", [[]])[0]
    retrieved_distances = res.get("distances", [[]])[0]

    books_found = []
    seen_titles = set()
    high_quality_count = 0

    for meta, dist in zip(retrieved_metas, retrieved_distances):
        if not meta:
            continue
        cosine_sim = max(0.0, 1.0 - float(dist)) if dist is not None else 0.70
        title = meta.get("title", "")
        t_key = title.lower().strip()
        if not t_key or t_key in seen_titles or is_bestseller_title(title):
            continue

        book_genre = meta.get("genre", "Fiction")
        # Ensure genre matches if active filter is set
        if active_genres:
            active_lower = [g.lower().strip() for g in active_genres]
            book_genre_lower = (book_genre or "").lower().strip()
            
            genres_list = []
            try:
                genres_list = [g.lower().strip() for g in json.loads(meta.get("genres_json", "[]"))]
            except Exception:
                pass
                
            categories_raw = (meta.get("categories", "") or "").lower()
            all_book_genres = {book_genre_lower} | set(genres_list)
            
            def matches_any_genre(active_list, b_genres, raw_cat):
                for ag in active_list:
                    if ag in b_genres:
                        return True, ag
                    if ag == 'fiction' and any('fiction' in bg and 'nonfiction' not in bg for bg in b_genres):
                        return True, 'Fiction'
                    if ag == 'nonfiction' and any('nonfiction' in bg for bg in b_genres):
                        return True, 'Nonfiction'
                    if ag == 'science fiction' and any('sci-fi' in bg or 'science fiction' in bg for bg in b_genres):
                        return True, 'Science Fiction'
                    if any(ag in bg or bg in ag for bg in b_genres):
                        return True, ag
                    if ag in raw_cat:
                        return True, ag
                return False, None

            is_match, matched_genre_name = matches_any_genre(active_lower, all_book_genres, categories_raw)
            if not is_match:
                continue
                
            # Use matching active genre name for display consistency
            for ag in active_genres:
                if ag.lower() == (matched_genre_name or '').lower() or ag.lower() in all_book_genres or ag.lower() in categories_raw:
                    book_genre = ag
                    break

        # COVER POLICY: Strictly require an authentic cover thumbnail or valid ISBN
        thumb_raw = meta.get("thumbnail", "")
        clean_isbn = re.sub(r'[^0-9X]', '', str(meta.get("isbn_13") or meta.get("isbn_10") or "")).strip()
        has_valid_isbn = len(clean_isbn) >= 9 and clean_isbn != "0"

        if thumb_raw and thumb_raw.startswith("http") and "/placeholder" not in thumb_raw and "cover-not-found" not in thumb_raw and "data:image" not in thumb_raw:
            thumb_final = thumb_raw
        elif has_valid_isbn:
            thumb_final = f"https://books.google.com/books/content?vid=ISBN{clean_isbn}&printsec=frontcover&img=1&zoom=1"
        else:
            # Skip books without cover
            continue

        seen_titles.add(t_key)

        # Calculate exact or near-exact title match boost
        q_tokens = [w for w in re.findall(r'[a-zA-Z0-9]+', clean_q.lower()) if len(w) > 2]
        t_tokens = [w for w in re.findall(r'[a-zA-Z0-9]+', title.lower()) if len(w) > 2]
        is_exact_title = clean_q.lower() == title.lower() or (len(q_tokens) >= 2 and all(w in t_tokens for w in q_tokens))
        
        effective_sim = max(cosine_sim, 0.96) if is_exact_title else cosine_sim

        if effective_sim >= min_similarity:
            high_quality_count += 1

        meta_rating = meta.get("rating")
        author_candidate = meta.get("authors", "Unknown Author")
        if meta_rating is not None and float(meta_rating) > 0 and round(float(meta_rating), 1) != 4.2:
            try:
                rating = round(float(meta_rating), 1)
            except Exception:
                rating = 4.5
        else:
            if is_famous_author(author_candidate):
                rating = 4.8
            else:
                h = sum(ord(c) for c in (title + author_candidate))
                rating = round(4.2 + ((h % 7) * 0.1), 1)

        percentage_score = min(99, max(70, int(effective_sim * 55 + 40 + (rating * 2.0))))

        book_obj = {
            "id": meta.get("id"),
            "title": title,
            "authors": meta.get("authors", "Unknown Author"),
            "description": meta.get("description", ""),
            "full_description": meta.get("full_description", ""),
            "thumbnail": thumb_final,
            "isbn": meta.get("isbn_13") or meta.get("isbn_10") or clean_isbn or None,
            "genre": book_genre,
            "simple_categories": book_genre,
            "categories": meta.get("categories", ""),
            "rating": rating,
            "source": meta.get("source", "Google Books"),
            "similarity": round(effective_sim, 3),
            "match_score": percentage_score,
            "links": {
                "info": meta.get("info_link", "") or f"https://www.google.com/search?q={title.replace(' ', '+')}",
                "preview": meta.get("preview_link", ""),
                "open_library": f"https://openlibrary.org/search?title={title.replace(' ', '+')}"
            }
        }
        books_found.append(book_obj)

    print(f"[Vector Search] Query: '{clean_q or 'browse'}' | Active Genres: {active_genres or 'None'} | Retrieved: {len(books_found)} | High-Quality Matches (sim >= {min_similarity:.2f}): {high_quality_count}")

    # 4. Dynamic Quality Evaluation
    if is_general_browse and len(books_found) >= limit:
        pass
    elif allow_dynamic_ingest and (high_quality_count < MIN_QUALITY_CANDIDATES or len(books_found) < 16):
        print(f"[Decision] Quality threshold unmet ({high_quality_count} < {MIN_QUALITY_CANDIDATES} matches, count={len(books_found)}). Calling Google Books API...")
        ingest_genre = active_genres[0] if active_genres else None
        api_query = clean_q if (clean_q and clean_q.lower() != 'popular') else (ingest_genre or "classic literature")
        
        ingest_res = ingestion_service.ingest_books(
            query=api_query,
            count=GOOGLE_BOOKS_MAX_RESULTS,
            genre_filter=ingest_genre
        )
        
        if ingest_res.get("imported", 0) > 0:
            print(f"[Unified Search] {ingest_res['imported']} new books ingested. Re-running vector search across unified collection...")
            return vector_search_books(
                query=query,
                target_genres=target_genres,
                limit=limit,
                min_similarity=min_similarity,
                allow_dynamic_ingest=False
            )
        else:
            print(f"[Decision] No new books imported from Google Books. Returning best existing vector results.")
    else:
        print(f"[Decision] Quality threshold satisfied ({high_quality_count} >= {MIN_QUALITY_CANDIDATES} high-quality matches). Google Books API NOT called.")

    # Sort unified results: exact/high similarity first, then rating
    books_found.sort(key=lambda b: (b.get("similarity", 0.70) * 2.0 + (b.get("rating", 4.2) * 0.1)), reverse=True)
    return books_found[:limit]


# ── REQUEST / RESPONSE MODELS ────────────────────────────────────────

class RecommendRequest(BaseModel):
    query: Optional[str] = "popular"
    category: Optional[str] = "All"
    categories: Optional[List[str]] = []
    tone: Optional[str] = "All"
    limit: Optional[int] = 120


class SimilarBooksRequest(BaseModel):
    title: str
    description: Optional[str] = ""
    genre: Optional[str] = ""
    isbn: Optional[str] = ""


class ImportBooksRequest(BaseModel):
    genre: Optional[str] = None
    query: Optional[str] = None
    count: Optional[int] = 20


class BookCreate(BaseModel):
    isbn13: Optional[int] = None
    title: str
    authors: str
    description: str
    thumbnail: Optional[str] = ""
    simple_categories: Optional[str] = ""
    joy: Optional[float] = 0.0
    surprise: Optional[float] = 0.0
    anger: Optional[float] = 0.0
    fear: Optional[float] = 0.0
    sadness: Optional[float] = 0.0


class BookUpdate(BaseModel):
    title: Optional[str] = None
    authors: Optional[str] = None
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    simple_categories: Optional[str] = None


# ── API ENDPOINTS ────────────────────────────────────────────────────

@app.get("/categories")
def get_categories():
    return {"categories": CURATED_GENRES}


@app.post("/recommend")
def recommend_books(req: RecommendRequest):
    query = (req.query or "").strip()
    selected_cats = [c.strip() for c in (req.categories or []) if c and c.strip() != "All"]
    if not selected_cats and req.category and req.category.strip() != "All":
        selected_cats = [req.category.strip()]

    # Vector similarity search in ChromaDB with on-demand Google Books ingestion
    books = vector_search_books(
        query=query,
        target_genres=selected_cats,
        limit=req.limit or 120,
        allow_dynamic_ingest=True
    )

    local_results = [b for b in books if b.get("source") == "BookMind Library"]
    external_results = [b for b in books if b.get("source") == "Google Books"]

    return {
        "query": query,
        "books": books,
        "local_results": local_results,
        "external_results": external_results,
        "total_results": len(books),
        "sources": {
            "local": len(local_results),
            "google_books": len(external_results),
            "vector_store_total": books_collection.count()
        }
    }


@app.get("/api/books/search")
async def search_books(
    q: str = Query("", description="Search term or natural language query"),
    category: Optional[str] = Query(None, description="Active single category"),
    genres: Optional[str] = Query(None, description="Comma-separated genres"),
    limit: int = Query(120, description="Max books limit")
):
    query = q.strip()
    target_genres = []
    if genres:
        target_genres = [g.strip() for g in genres.split(",") if g.strip() and g.strip() != "All"]
    elif category and category.strip() != "All":
        target_genres = [category.strip()]

    if not query and not target_genres:
        # Default browse (All)
        books = vector_search_books(query="popular", limit=limit or 120, allow_dynamic_ingest=False)
    else:
        books = vector_search_books(query=query, target_genres=target_genres, limit=limit or 120, allow_dynamic_ingest=True)

    local_matches = [b for b in books if b.get("source") == "BookMind Library"]
    external_matches = [b for b in books if b.get("source") == "Google Books"]

    return {
        "query": query,
        "books": books,
        "local_results": local_matches,
        "external_results": external_matches,
        "total_results": len(books),
        "sources": {
            "local": len(local_matches),
            "google_books": len(external_matches)
        }
    }


@app.post("/api/books/similar")
def get_similar_books(req: SimilarBooksRequest):
    """Vector similarity search to find semantically matching books."""
    title = req.title.strip()
    desc = (req.description or "").strip()
    genre = (req.genre or "").strip()

    search_query = f"{title} by {genre}. Themes and style: {desc}"
    query_vec = get_or_create_query_embedding(search_query)

    where_clause = {"genre": genre} if genre and genre != "All" else None

    try:
        res = books_collection.query(
            query_embeddings=[query_vec],
            n_results=15,
            where=where_clause,
            include=["metadatas", "distances"]
        )
    except Exception:
        res = books_collection.query(
            query_embeddings=[query_vec],
            n_results=15,
            include=["metadatas", "distances"]
        )

    retrieved_metas = res.get("metadatas", [[]])[0]
    retrieved_distances = res.get("distances", [[]])[0]

    similar = []
    seen = {title.lower().strip()}
    high_quality_similar = 0

    for meta, dist in zip(retrieved_metas, retrieved_distances):
        if not meta:
            continue
        t_clean = meta.get("title", "").strip()
        if not t_clean or t_clean.lower() in seen or is_bestseller_title(t_clean):
            continue
        seen.add(t_clean.lower())

        thumb = meta.get("thumbnail", "")
        if not thumb or not thumb.startswith("http") or "/placeholder.svg" in thumb or "cover-not-found" in thumb:
            continue

        cosine_sim = max(0.0, 1.0 - float(dist)) if dist is not None else 0.75
        if cosine_sim >= SIMILAR_THRESHOLD:
            high_quality_similar += 1

        rating = float(meta.get("rating", 4.5))
        percentage = min(98, max(72, int(cosine_sim * 60 + 45 + (rating * 2.0))))

        similar.append({
            "id": meta.get("id"),
            "title": t_clean,
            "authors": meta.get("authors", "Unknown Author"),
            "description": meta.get("description", ""),
            "full_description": meta.get("full_description", ""),
            "thumbnail": thumb,
            "isbn": meta.get("isbn_13") or meta.get("isbn_10") or None,
            "genre": meta.get("genre", "Fiction"),
            "rating": rating,
            "source": meta.get("source", "BookMind Library"),
            "score": percentage,
            "similarity": round(cosine_sim, 3),
            "links": {
                "info": meta.get("info_link", "") or f"https://www.google.com/search?q={t_clean.replace(' ', '+')}",
                "preview": meta.get("preview_link", "")
            }
        })
        if len(similar) >= 5:
            break

    print(f"[Similar Books] Target: '{title}' ({genre}) | Found: {len(similar)} | High-Quality (sim >= {SIMILAR_THRESHOLD}): {high_quality_similar}")

    # Evaluate quality of similar matches: Only fetch if insufficient high quality matches
    if high_quality_similar < SIMILAR_MIN_QUALITY:
        print(f"[Similar Books] High-quality candidates below threshold ({high_quality_similar} < {SIMILAR_MIN_QUALITY}). Calling Google Books...")
        ingest_res = ingestion_service.ingest_books(
            query=f"{title} {genre}",
            count=10,
            genre_filter=genre if genre != "All" else None
        )
        if ingest_res.get("imported", 0) > 0:
            # Re-query
            return get_similar_books(req)
    else:
        print(f"[Similar Books] High-quality candidates sufficient ({high_quality_similar} >= {SIMILAR_MIN_QUALITY}). Google Books NOT called.")

    return {
        "source_book": title,
        "recommendations": similar[:5]
    }


@app.get("/api/books/suggest")
async def suggest_books(q: str):
    """Fast autocomplete suggestions using vector store and title index."""
    query = q.strip()
    if not query or len(query) < 2:
        return {"suggestions": []}

    suggestions = []
    seen_titles = set()
    q_lower = query.lower()

    # Search in ChromaDB metadata
    try:
        data = books_collection.get(include=["metadatas"], limit=1000)
        for m in data.get("metadatas", []):
            if not m:
                continue
            title = m.get("title", "")
            authors = m.get("authors", "")
            thumb = m.get("thumbnail", "")
            if not thumb or not thumb.startswith("http") or "/placeholder.svg" in thumb or "cover-not-found" in thumb:
                continue
            if is_bestseller_title(title):
                continue
            if q_lower in title.lower() or q_lower in authors.lower():
                t_lower = title.lower()
                if t_lower not in seen_titles:
                    seen_titles.add(t_lower)
                    suggestions.append({
                        "title": title,
                        "author": authors,
                        "genre": m.get("genre", "Fiction"),
                        "thumbnail": thumb,
                        "isbn": m.get("isbn_13") or m.get("isbn_10") or ""
                    })
                    if len(suggestions) >= 6:
                        break
    except Exception as e:
        print(f"Error fetching suggestions from ChromaDB: {e}")

    # Fallback to Google Books intitle if sparse
    if len(suggestions) < 5:
        try:
            params = {"q": f"intitle:{query}", "maxResults": 10, "langRestrict": "en"}
            api_key = os.getenv("GOOGLE_BOOKS_API_KEY")
            if api_key:
                params["key"] = api_key
            async with httpx.AsyncClient() as client:
                resp = await client.get("https://www.googleapis.com/books/v1/volumes", params=params, timeout=3.0)
                if resp.status_code == 200:
                    items = resp.json().get("items", [])
                    for it in items:
                        vol = it.get("volumeInfo", {})
                        t = vol.get("title", "").strip()
                        t_lower = t.lower()
                        if is_bestseller_title(t):
                            continue
                        img_links = vol.get("imageLinks", {})
                        thumb = img_links.get("thumbnail") or img_links.get("smallThumbnail") or ""
                        if not thumb or not thumb.startswith("http"):
                            continue
                        if t and t_lower not in seen_titles:
                            seen_titles.add(t_lower)
                            authors = ", ".join(vol.get("authors", [])) or "Unknown Author"
                            cats = vol.get("categories", ["Fiction"])
                            suggestions.append({
                                "title": t,
                                "author": authors,
                                "genre": cats[0] if cats else "Fiction",
                                "thumbnail": thumb,
                                "isbn": ""
                            })
                            if len(suggestions) >= 8:
                                break
        except Exception as e:
            print(f"Google books suggestion error: {e}")

    return {"suggestions": suggestions[:8]}


@app.api_route("/api/books/cover", methods=["GET", "HEAD"])
async def get_book_cover(
    title: str = Query("", description="Title of the book"),
    author: str = Query("", description="Author of the book"),
    isbn: Optional[str] = Query(None, description="ISBN-10 or ISBN-13")
):
    """
    Dynamic cascading cover resolution endpoint.
    Redirects to the best available retail photo cover image (Google Content CDN, OpenLibrary, or fallback).
    """
    clean_isbn = re.sub(r'[^0-9X]', '', str(isbn or '')).strip()
    if clean_isbn and len(clean_isbn) >= 9 and clean_isbn != "0":
        return RedirectResponse(
            url=f"https://books.google.com/books/content?vid=ISBN{clean_isbn}&printsec=frontcover&img=1&zoom=1",
            status_code=307
        )

    # Try resolve authentic cover via OpenLibrary search / cache
    real_cover = resolve_authentic_cover(title=title, author=author or "", isbn_13=clean_isbn)
    if real_cover and real_cover.startswith("http"):
        return RedirectResponse(url=real_cover, status_code=307)

    # Fallback to OpenLibrary generic title search
    clean_t = re.split(r'[:\-\(]', title)[0].strip()
    if clean_t:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://openlibrary.org/search.json",
                    params={"title": clean_t, "limit": 2},
                    headers={"User-Agent": "BookMind/2.0"},
                    timeout=2.5
                )
                if resp.status_code == 200:
                    docs = resp.json().get("docs", [])
                    if docs:
                        cid = docs[0].get("cover_i")
                        if cid:
                            return RedirectResponse(url=f"https://covers.openlibrary.org/b/id/{cid}-L.jpg", status_code=307)
                        isbns = docs[0].get("isbn", [])
                        if isbns:
                            clean_doc_isbn = re.sub(r'[^0-9X]', '', isbns[0]).strip()
                            if clean_doc_isbn:
                                return RedirectResponse(
                                    url=f"https://books.google.com/books/content?vid=ISBN{clean_doc_isbn}&printsec=frontcover&img=1&zoom=1",
                                    status_code=307
                                )
        except Exception:
            pass

    raise HTTPException(status_code=404, detail="No authentic cover found")


@app.post("/api/books/import")
def api_import_books(req: ImportBooksRequest):
    """Admin endpoint to trigger dynamic book ingestion from Google Books."""
    query_str = req.query or req.genre or "classic literature"
    result = ingestion_service.ingest_books(
        query=query_str,
        count=req.count or 20,
        genre_filter=req.genre
    )
    return result


@app.get("/api/books/stats")
def get_library_stats():
    """Get statistics about the ChromaDB vector database."""
    total_count = books_collection.count()
    return {
        "total_books_in_vector_store": total_count,
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "embedding_dimensions": 384,
        "distance_metric": "cosine",
        "collection_name": books_collection.name,
        "curated_genres_count": len(CURATED_GENRES) - 1
    }


# ── ADMIN & GEMINI VISION ENDPOINTS ──────────────────────────────────

@app.get("/admin/books")
def admin_get_books():
    if supabase:
        try:
            data = supabase.table("books").select("id, isbn13, title, authors, thumbnail, simple_categories, description").order("id", desc=True).execute().data
            return {"books": data}
        except Exception as e:
            print(f"Supabase admin error: {e}")
    # Return from ChromaDB
    res = books_collection.get(include=["metadatas"], limit=50)
    return {"books": res.get("metadatas", [])}


@app.post("/admin/books")
def admin_add_book(book: BookCreate):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    
    embedding_model = get_embedding_model()
    embedding = embedding_model.encode([f"{book.title} by {book.authors}. {book.description}"], normalize_embeddings=True)[0].tolist()

    record = book.model_dump()
    if embedding:
        record["embedding"] = embedding
    result = supabase.table("books").insert(record).execute()
    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to add book")
    return {"message": "Book added successfully", "book": result.data[0]}


@app.put("/admin/books/{book_id}")
def admin_update_book(book_id: int, book: BookUpdate):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    updates = {k: v for k, v in book.model_dump().items() if v is not None}
    result = supabase.table("books").update(updates).eq("id", book_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book updated successfully"}


@app.delete("/admin/books/{book_id}")
def admin_delete_book(book_id: int):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    result = supabase.table("books").delete().eq("id", book_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted successfully"}


@app.post("/summarize-cover")
async def summarize_cover(
    file: Optional[UploadFile] = File(None),
    image_url: Optional[str] = Form(None)
):
    if not gemini_model:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")

    try:
        if file:
            image_bytes = await file.read()
            mime_type = file.content_type or "image/jpeg"
            image_part = {"mime_type": mime_type, "data": image_bytes}
        elif image_url:
            async with httpx.AsyncClient() as client:
                resp = await client.get(image_url, timeout=10)
                resp.raise_for_status()
            image_bytes = resp.content
            mime_type = resp.headers.get("content-type", "image/jpeg").split(";")[0]
            image_part = {"mime_type": mime_type, "data": image_bytes}
        else:
            raise HTTPException(status_code=400, detail="Provide either a file upload or image_url")

        prompt = (
            "You are a book expert. Analyze this book cover image and provide:\n"
            "1. Title (if visible)\n"
            "2. Author (if visible)\n"
            "3. Genre\n"
            "4. A 3-4 sentence summary of what this book is likely about based on the cover design, imagery, title, and any text visible.\n"
            "Format your response as JSON with keys: title, author, genre, summary."
        )

        response = gemini_model.generate_content([prompt, image_part])
        text = response.text.strip()

        if text.startswith("```"):
            text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

        result = json.loads(text)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)
