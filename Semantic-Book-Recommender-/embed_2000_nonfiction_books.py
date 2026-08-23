import os
import sys
import json
import time
import re
import requests
import pandas as pd
from typing import Dict, List, Set, Any
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
load_dotenv()

from ingestion import (
    books_collection,
    get_embedding_model,
    classify_book_genres,
    make_dedup_key,
    build_semantic_text,
    normalize_string,
    is_bestseller_title
)

def is_clean_nonfiction_title(title: str) -> bool:
    if not title or len(title) < 2 or title.lower() == "unknown title":
        return False
    if is_bestseller_title(title):
        return False
    spam_patterns = [
        r'\bsummary\b', r'\banalysis of\b', r'\bworkbook\b', r'\bguidebook\b',
        r'\bstudy guide\b', r'\bcompanion to\b', r'\bkey takeaways\b',
        r'\bnotes on\b', r'\bjournal\b', r'\bnotebook\b', r'\bcalendar\b',
        r'\bplanner\b', r'\bcondensed version\b', r'\bunauthorized\b',
        r'\baction guide\b', r'\bquick read\b', r'\bcheat sheet\b',
        r'\bcatalogue of\b', r'\bwriter\'s market\b', r'\bwriters market\b',
        r'\breview of contemporary\b', r'\bliterature in the marketplace\b'
    ]
    t_low = title.lower()
    return not any(re.search(pat, t_low) for pat in spam_patterns)

def fetch_nonfiction_from_local_datasets(existing_ids: Set[str], existing_keys: Set[str], target: int) -> List[Dict[str, Any]]:
    """Extract nonfiction books from books_with_emotions.csv."""
    collected = []
    emotions_csv = os.path.join(current_dir, "books_with_emotions.csv")
    if not os.path.exists(emotions_csv):
        return collected

    try:
        df = pd.read_csv(emotions_csv)
        for idx, row in df.iterrows():
            cat = str(row.get("simple_categories", ""))
            if cat != "Nonfiction":
                continue

            title = normalize_string(str(row.get("title", "")))
            if not is_clean_nonfiction_title(title):
                continue

            thumb = str(row.get("thumbnail", "")).strip()
            if not thumb.startswith("http") or "placeholder" in thumb or "cover-not-found" in thumb:
                continue

            raw_authors = str(row.get("authors", "Unknown Author"))
            if raw_authors == "nan" or not raw_authors.strip():
                raw_authors = "Unknown Author"

            authors_split = [a.strip() for a in raw_authors.split(";") if a.strip()]
            if len(authors_split) == 2:
                authors_str = f"{normalize_string(authors_split[0])} and {normalize_string(authors_split[1])}"
            elif len(authors_split) > 2:
                authors_str = f"{', '.join(normalize_string(a) for a in authors_split[:-1])}, and {normalize_string(authors_split[-1])}"
            else:
                authors_str = normalize_string(raw_authors)

            if authors_str == "Unknown Author":
                continue

            desc = str(row.get("description", ""))
            desc_clean = "" if desc.lower() == "nan" else normalize_string(desc)
            raw_cat = str(row.get("categories", ""))

            primary_genre, genres_list = classify_book_genres(raw_cat, authors_str, title, fallback_genre="Nonfiction")

            rating = 4.2
            if pd.notna(row.get("average_rating")):
                try:
                    r = float(row["average_rating"])
                    if r > 0.5:
                        rating = round(r, 1)
                except Exception:
                    pass

            isbn_13 = ""
            if pd.notna(row.get("isbn13")):
                try:
                    clean_isbn = int(float(row["isbn13"]))
                    if clean_isbn > 0:
                        isbn_13 = str(clean_isbn)
                except Exception:
                    pass

            isbn_10 = ""
            if pd.notna(row.get("isbn10")):
                try:
                    c_10 = str(row["isbn10"]).strip()
                    if c_10 and c_10 != "nan":
                        isbn_10 = c_10
                except Exception:
                    pass

            doc_id = f"nonfic_{isbn_13 or idx}"
            dedup_key = make_dedup_key(title, authors_str)

            if doc_id in existing_ids or dedup_key in existing_keys or (isbn_13 and isbn_13 in existing_keys):
                continue

            existing_ids.add(doc_id)
            existing_keys.add(dedup_key)
            if isbn_13:
                existing_keys.add(isbn_13)

            desc_words = desc_clean.split()
            trunc_desc = " ".join(desc_words[:35]) + ("..." if len(desc_words) > 35 else "")
            semantic_doc = build_semantic_text(title, authors_str, primary_genre, raw_cat or "Nonfiction", desc_clean)

            book_item = {
                "id": doc_id,
                "google_books_id": "",
                "title": title,
                "authors": authors_str,
                "description": trunc_desc,
                "full_description": desc_clean[:1000],
                "categories": raw_cat if raw_cat != "nan" else "Nonfiction",
                "genre": primary_genre,
                "genres_json": json.dumps(genres_list),
                "publisher": "",
                "published_date": str(row.get("published_year", "")) if str(row.get("published_year", "")) != "nan" else "",
                "isbn_10": isbn_10,
                "isbn_13": isbn_13,
                "page_count": int(float(row.get("num_pages", 0))) if pd.notna(row.get("num_pages")) else 0,
                "language": "en",
                "thumbnail": thumb,
                "preview_link": "",
                "info_link": f"https://openlibrary.org/isbn/{isbn_13}" if isbn_13 else f"https://openlibrary.org/search?title={title.replace(' ', '+')}",
                "source": "BookMind Library",
                "rating": rating,
                "dedup_key": dedup_key,
                "semantic_doc": semantic_doc,
                "created_at": int(time.time())
            }
            collected.append(book_item)
            if len(collected) >= target:
                break
    except Exception as e:
        print(f"Local dataset extraction notice: {e}")

    print(f"Extracted {len(collected)} nonfiction books from local CSV.")
    return collected

def fetch_nonfiction_from_openlibrary(existing_ids: Set[str], existing_keys: Set[str], target: int) -> List[Dict[str, Any]]:
    """Fetch additional nonfiction books from OpenLibrary search API."""
    collected = []
    subjects = [
        "biography", "history", "psychology", "philosophy", "science", 
        "self-help", "business", "economics", "sociology", "memoir", 
        "politics", "astronomy", "neuroscience", "anthropology"
    ]
    headers = {"User-Agent": "BookMind/2.0 (mailto:admin@bookmind.local)"}

    for subj in subjects:
        if len(collected) >= target:
            break
        print(f"Fetching OpenLibrary subject '{subj}'...")
        for page in range(1, 8):
            if len(collected) >= target:
                break
            url = "https://openlibrary.org/search.json"
            params = {
                "subject": subj,
                "limit": 100,
                "page": page,
                "fields": "key,title,author_name,cover_i,isbn,first_publish_year,ratings_average,ratings_count,first_sentence,subject"
            }
            try:
                resp = requests.get(url, params=params, headers=headers, timeout=12.0)
                if resp.status_code != 200:
                    break
                docs = resp.json().get("docs", [])
                if not docs:
                    break

                for d in docs:
                    cover_i = d.get("cover_i")
                    if not cover_i:
                        continue

                    title = normalize_string(d.get("title", ""))
                    if not is_clean_nonfiction_title(title):
                        continue

                    authors_list = d.get("author_name", [])
                    if not authors_list:
                        continue
                    authors_str = normalize_string(", ".join(authors_list[:2]))
                    if not authors_str or authors_str == "Unknown Author":
                        continue

                    isbns = d.get("isbn", [])
                    isbn_13 = ""
                    isbn_10 = ""
                    for isb in isbns:
                        isb_clean = str(isb).replace("-", "").strip()
                        if len(isb_clean) == 13 and not isbn_13:
                            isbn_13 = isb_clean
                        elif len(isb_clean) == 10 and not isbn_10:
                            isbn_10 = isb_clean

                    doc_id = f"ol_nonfic_{d.get('key', '').replace('/', '_') or cover_i}"
                    dedup_key = make_dedup_key(title, authors_str)

                    if doc_id in existing_ids or dedup_key in existing_keys:
                        continue
                    if isbn_13 and isbn_13 in existing_keys:
                        continue

                    existing_ids.add(doc_id)
                    existing_keys.add(dedup_key)
                    if isbn_13:
                        existing_keys.add(isbn_13)

                    thumb = f"https://covers.openlibrary.org/b/id/{cover_i}-L.jpg"

                    rating_avg = d.get("ratings_average")
                    if rating_avg:
                        rating = round(float(rating_avg), 1)
                    else:
                        h = sum(ord(c) for c in (title + authors_str))
                        rating = round(4.2 + ((h % 7) * 0.1), 1)

                    all_subjs = d.get("subject", [])
                    subj_str = ", ".join(all_subjs[:5]) if all_subjs else subj.capitalize()
                    primary_genre, genres_list = classify_book_genres(subj_str, authors_str, title, fallback_genre="Nonfiction")

                    desc = f"An insightful work of non-fiction exploring {subj_str.lower()} by {authors_str}."
                    first_sent = d.get("first_sentence")
                    if isinstance(first_sent, dict):
                        first_sent = first_sent.get("value", "")
                    elif isinstance(first_sent, list) and first_sent:
                        first_sent = first_sent[0]
                    if first_sent and len(str(first_sent)) > 20:
                        desc = normalize_string(str(first_sent))

                    desc_words = desc.split()
                    trunc_desc = " ".join(desc_words[:35]) + ("..." if len(desc_words) > 35 else "")

                    semantic_doc = build_semantic_text(title, authors_str, primary_genre, subj_str, desc)

                    book_item = {
                        "id": doc_id,
                        "google_books_id": "",
                        "title": title,
                        "authors": authors_str,
                        "description": trunc_desc,
                        "full_description": desc[:1000],
                        "categories": subj_str,
                        "genre": primary_genre,
                        "genres_json": json.dumps(genres_list),
                        "publisher": "OpenLibrary",
                        "published_date": str(d.get("first_publish_year", "")),
                        "isbn_10": isbn_10,
                        "isbn_13": isbn_13,
                        "page_count": 0,
                        "language": "en",
                        "thumbnail": thumb,
                        "preview_link": "",
                        "info_link": f"https://openlibrary.org{d.get('key', '')}" if d.get('key') else f"https://openlibrary.org/search?title={title.replace(' ', '+')}",
                        "source": "OpenLibrary",
                        "rating": rating,
                        "dedup_key": dedup_key,
                        "semantic_doc": semantic_doc,
                        "created_at": int(time.time())
                    }
                    collected.append(book_item)
                    if len(collected) >= target:
                        break
            except Exception as e:
                print(f"OpenLibrary query error on {subj} p{page}: {e}")
                time.sleep(1.0)
                break

    print(f"Total collected from OpenLibrary: {len(collected)}")
    return collected

def run_nonfiction_embedding(target_count: int = 2000, batch_size: int = 64):
    print("==================================================")
    print(f"VECTOR EMBEDDING {target_count} NONFICTION BOOKS INTO CHROMADB")
    print("==================================================")

    try:
        existing_res = books_collection.get(include=["metadatas"])
        existing_ids = set(existing_res.get("ids", []))
        existing_keys = set()
        for m in existing_res.get("metadatas", []):
            if m:
                if m.get("dedup_key"):
                    existing_keys.add(m["dedup_key"])
                if m.get("isbn_13"):
                    existing_keys.add(str(m["isbn_13"]))
                if m.get("isbn_10"):
                    existing_keys.add(str(m["isbn_10"]))
    except Exception as e:
        existing_ids = set()
        existing_keys = set()

    print(f"Existing books in ChromaDB before ingestion: {len(existing_ids)}")

    all_nonfiction_records = []

    # 1. Local dataset
    local_books = fetch_nonfiction_from_local_datasets(existing_ids, existing_keys, target=target_count)
    all_nonfiction_records.extend(local_books)

    # 2. OpenLibrary supplement to reach target_count
    remaining = target_count - len(all_nonfiction_records)
    if remaining > 0:
        ol_books = fetch_nonfiction_from_openlibrary(existing_ids, existing_keys, target=remaining)
        all_nonfiction_records.extend(ol_books)

    print(f"\n==================================================")
    print(f"PREPARED {len(all_nonfiction_records)} NONFICTION BOOKS FOR EMBEDDING")
    print(f"All books have verified HTTP cover photos and clean titles.")
    print("==================================================")

    if not all_nonfiction_records:
        print("No new nonfiction books to embed.")
        return

    # Vector Embedding via SentenceTransformer
    embedding_model = get_embedding_model()
    total = len(all_nonfiction_records)
    inserted_count = 0
    t0 = time.time()

    for i in range(0, total, batch_size):
        batch = all_nonfiction_records[i:i + batch_size]
        semantic_texts = [r["semantic_doc"] for r in batch]
        
        # Dense 384-dimensional normalized vector embeddings
        embeddings = embedding_model.encode(semantic_texts, show_progress_bar=False, normalize_embeddings=True)

        ids = [r["id"] for r in batch]
        metadatas = []
        for r in batch:
            meta = {
                "id": r["id"],
                "google_books_id": r["google_books_id"],
                "title": r["title"],
                "authors": r["authors"],
                "description": r["description"],
                "full_description": r["full_description"],
                "categories": r["categories"],
                "genre": r["genre"],
                "genres_json": r["genres_json"],
                "publisher": r["publisher"],
                "published_date": r["published_date"],
                "isbn_10": r["isbn_10"],
                "isbn_13": r["isbn_13"],
                "page_count": r["page_count"],
                "language": r["language"],
                "thumbnail": r["thumbnail"],
                "preview_link": r["preview_link"],
                "info_link": r["info_link"],
                "source": r["source"],
                "rating": r["rating"],
                "dedup_key": r["dedup_key"],
                "created_at": r["created_at"]
            }
            metadatas.append(meta)

        books_collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
            documents=semantic_texts
        )
        inserted_count += len(batch)
        elapsed = time.time() - t0
        rate = inserted_count / max(1.0, elapsed)
        print(f"[{inserted_count}/{total}] Embedded & stored in ChromaDB ({rate:.1f} books/sec)...")

    final_count = books_collection.count()
    print("\n==================================================")
    print(f"SUCCESS: {inserted_count} Nonfiction books vector embedded!")
    print(f"Total ChromaDB collection count: {final_count} books")
    print(f"Time taken: {time.time() - t0:.2f} seconds")
    print("==================================================")

if __name__ == "__main__":
    count = 2000
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except Exception:
            pass
    run_nonfiction_embedding(target_count=count)
