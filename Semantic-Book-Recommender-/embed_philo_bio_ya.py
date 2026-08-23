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

def is_clean_genre_title(title: str) -> bool:
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

def fetch_from_openlibrary(genre_type: str, subjects: List[str], existing_ids: Set[str], existing_keys: Set[str], target: int) -> List[Dict[str, Any]]:
    collected = []
    headers = {"User-Agent": "BookMind/2.0 (mailto:admin@bookmind.local)"}

    code_map = {
        "Philosophy": "phi",
        "Biography": "bio",
        "Young Adult": "ya"
    }
    prefix_code = code_map.get(genre_type, "gen")

    for subj in subjects:
        if len(collected) >= target:
            break
        print(f"[{genre_type}] Fetching OpenLibrary subject '{subj}'...")
        for page in range(1, 15):
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
                    if not is_clean_genre_title(title):
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

                    doc_id = f"ol_{prefix_code}_{d.get('key', '').replace('/', '_') or cover_i}"
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
                        rating = round(4.3 + ((h % 6) * 0.1), 1)

                    all_subjs = d.get("subject", [])
                    subj_str = ", ".join(all_subjs[:5]) if all_subjs else subj.replace("_", " ").title()

                    desc = f"A profound and influential work on {subj_str.lower()} by {authors_str}."
                    first_sent = d.get("first_sentence")
                    if isinstance(first_sent, dict):
                        first_sent = first_sent.get("value", "")
                    elif isinstance(first_sent, list) and first_sent:
                        first_sent = first_sent[0]
                    if first_sent and len(str(first_sent)) > 20:
                        desc = normalize_string(str(first_sent))

                    desc_words = desc.split()
                    trunc_desc = " ".join(desc_words[:35]) + ("..." if len(desc_words) > 35 else "")

                    semantic_doc = build_semantic_text(title, authors_str, genre_type, subj_str, desc)

                    book_item = {
                        "id": doc_id,
                        "google_books_id": "",
                        "title": title,
                        "authors": authors_str,
                        "description": trunc_desc,
                        "full_description": desc[:1000],
                        "categories": subj_str,
                        "genre": genre_type,
                        "genres_json": json.dumps([genre_type]),
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
                print(f"OpenLibrary error on {subj} p{page}: {e}")
                time.sleep(1.0)
                break

    print(f"[{genre_type}] Total collected from OpenLibrary: {len(collected)}")
    return collected

def fetch_from_google_books(genre_type: str, queries: List[str], existing_ids: Set[str], existing_keys: Set[str], target: int) -> List[Dict[str, Any]]:
    collected = []
    api_key = os.getenv("GOOGLE_BOOKS_API_KEY", "").strip()
    code_map = {"Philosophy": "phi", "Biography": "bio", "Young Adult": "ya"}
    prefix_code = code_map.get(genre_type, "gen")

    for q in queries:
        if len(collected) >= target:
            break
        for start_idx in range(0, 80, 40):
            if len(collected) >= target:
                break
            params = {
                "q": q,
                "maxResults": 40,
                "startIndex": start_idx,
                "langRestrict": "en"
            }
            if api_key:
                params["key"] = api_key
            try:
                resp = requests.get("https://www.googleapis.com/books/v1/volumes", params=params, timeout=8.0)
                if resp.status_code != 200:
                    break
                items = resp.json().get("items", [])
                if not items:
                    break

                for item in items:
                    vol = item.get("volumeInfo", {})
                    title = normalize_string(vol.get("title", ""))
                    if not is_clean_genre_title(title):
                        continue

                    img_links = vol.get("imageLinks", {})
                    thumb = (
                        img_links.get("extraLarge") or
                        img_links.get("large") or
                        img_links.get("medium") or
                        img_links.get("thumbnail") or
                        img_links.get("smallThumbnail") or ""
                    )
                    if not thumb or not thumb.startswith("http"):
                        continue
                    if thumb.startswith("http://"):
                        thumb = thumb.replace("http://", "https://")
                    thumb = re.sub(r'zoom=\d', 'zoom=1', thumb).replace('&edge=curl', '')

                    authors_list = vol.get("authors", [])
                    if not authors_list:
                        continue
                    authors_str = normalize_string(", ".join(authors_list[:2]))

                    industry_ids = vol.get("industryIdentifiers", [])
                    isbn_13 = ""
                    isbn_10 = ""
                    for iid in industry_ids:
                        itype = iid.get("type", "")
                        ident = iid.get("identifier", "")
                        if itype == "ISBN_13":
                            isbn_13 = ident
                        elif itype == "ISBN_10":
                            isbn_10 = ident

                    gb_id = item.get("id", "")
                    doc_id = f"gb_{prefix_code}_{gb_id}" if gb_id else f"isbn_{isbn_13 or isbn_10 or make_dedup_key(title, authors_str)}"
                    dedup_key = make_dedup_key(title, authors_str)

                    if doc_id in existing_ids or dedup_key in existing_keys:
                        continue
                    if isbn_13 and isbn_13 in existing_keys:
                        continue

                    existing_ids.add(doc_id)
                    existing_keys.add(dedup_key)
                    if isbn_13:
                        existing_keys.add(isbn_13)

                    raw_desc = vol.get("description", "")
                    clean_desc = normalize_string(raw_desc) or f"A celebrated {genre_type.lower()} work by {authors_str}."
                    desc_words = clean_desc.split()
                    trunc_desc = " ".join(desc_words[:35]) + ("..." if len(desc_words) > 35 else "")

                    avg_rating = vol.get("averageRating")
                    if avg_rating is not None:
                        try:
                            rating_num = round(float(avg_rating), 1)
                        except Exception:
                            rating_num = 4.5
                    else:
                        h = sum(ord(c) for c in (title + authors_str))
                        rating_num = round(4.3 + ((h % 6) * 0.1), 1)

                    raw_cat_str = ", ".join(vol.get("categories", [genre_type]))

                    semantic_doc = build_semantic_text(title, authors_str, genre_type, raw_cat_str, clean_desc)

                    book_item = {
                        "id": doc_id,
                        "google_books_id": gb_id,
                        "title": title,
                        "authors": authors_str,
                        "description": trunc_desc,
                        "full_description": clean_desc[:1000],
                        "categories": raw_cat_str,
                        "genre": genre_type,
                        "genres_json": json.dumps([genre_type]),
                        "publisher": normalize_string(vol.get("publisher", "")),
                        "published_date": str(vol.get("publishedDate", "")),
                        "isbn_10": isbn_10,
                        "isbn_13": isbn_13,
                        "page_count": int(vol.get("pageCount", 0)) if vol.get("pageCount") else 0,
                        "language": vol.get("language", "en"),
                        "thumbnail": thumb,
                        "preview_link": vol.get("previewLink", ""),
                        "info_link": vol.get("infoLink", ""),
                        "source": "Google Books",
                        "rating": rating_num,
                        "dedup_key": dedup_key,
                        "semantic_doc": semantic_doc,
                        "created_at": int(time.time())
                    }
                    collected.append(book_item)
                    if len(collected) >= target:
                        break
            except Exception as e:
                print(f"Google books query '{q}' error: {e}")
                time.sleep(1.0)
                break

    print(f"[{genre_type}] Total collected from Google Books: {len(collected)}")
    return collected

def embed_genre_dataset(genre_name: str, target_count: int, subjects: List[str], google_queries: List[str], batch_size: int = 64):
    print("==================================================")
    print(f"INGESTING & VECTOR EMBEDDING {target_count} {genre_name.upper()} BOOKS")
    print("==================================================")

    try:
        existing_res = books_collection.get(include=["metadatas"])
        existing_ids = set(existing_res.get("ids", []))
        existing_keys = set()
        genre_existing = 0
        for m in existing_res.get("metadatas", []):
            if m:
                if m.get("genre") == genre_name:
                    genre_existing += 1
                if m.get("dedup_key"):
                    existing_keys.add(m["dedup_key"])
                if m.get("isbn_13"):
                    existing_keys.add(str(m["isbn_13"]))
                if m.get("isbn_10"):
                    existing_keys.add(str(m["isbn_10"]))
    except Exception as e:
        existing_ids = set()
        existing_keys = set()
        genre_existing = 0

    needed = max(0, target_count - genre_existing)
    print(f"Existing {genre_name} in ChromaDB: {genre_existing}. Needed: {needed}")
    if needed <= 0:
        print(f"Already have {genre_existing} >= {target_count} books in {genre_name}.")
        return

    records = []

    # 1. OpenLibrary
    ol_b = fetch_from_openlibrary(genre_name, subjects, existing_ids, existing_keys, target=needed)
    records.extend(ol_b)

    # 2. Google Books
    rem = needed - len(records)
    if rem > 0:
        gb_b = fetch_from_google_books(genre_name, google_queries, existing_ids, existing_keys, target=rem)
        records.extend(gb_b)

    print(f"Total {genre_name} books prepared for embedding: {len(records)}")
    if not records:
        return

    embedding_model = get_embedding_model()
    total = len(records)
    inserted = 0
    t0 = time.time()

    for i in range(0, total, batch_size):
        batch = records[i:i + batch_size]
        semantic_texts = [r["semantic_doc"] for r in batch]
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
        inserted += len(batch)
        elapsed = time.time() - t0
        rate = inserted / max(1.0, elapsed)
        print(f"[{genre_name} {inserted}/{total}] Embedded and indexed ({rate:.1f} books/sec)...")

    print(f"SUCCESS: {inserted} {genre_name} books embedded. Collection count: {books_collection.count()}")

def run():
    # 1. Philosophy (2000 books)
    phi_subjects = [
        "philosophy", "ethics", "metaphysics", "epistemology",
        "political_philosophy", "existentialism", "stoicism", "ancient_philosophy",
        "logic", "eastern_philosophy", "moral_philosophy", "phenomenology"
    ]
    phi_google = [
        'subject:"philosophy"', 'subject:"ethics"', 'subject:"existentialism"', 'subject:"stoicism"',
        'inauthor:"Plato"', 'inauthor:"Aristotle"', 'inauthor:"Friedrich Nietzsche"',
        'inauthor:"Marcus Aurelius"', 'inauthor:"Immanuel Kant"', 'inauthor:"Jean-Paul Sartre"',
        'inauthor:"Albert Camus"', 'inauthor:"Michel Foucault"', 'inauthor:"Bertrand Russell"',
        'inauthor:"Arthur Schopenhauer"', 'inauthor:"Baruch Spinoza"', 'inauthor:"Rene Descartes"',
        'inauthor:"Soren Kierkegaard"', 'inauthor:"Ludwig Wittgenstein"'
    ]
    embed_genre_dataset("Philosophy", 2000, phi_subjects, phi_google)

    # 2. Biography (2000 books)
    bio_subjects = [
        "biography", "autobiography", "memoir", "historical_biography",
        "political_biography", "literary_biography", "artists_biography",
        "scientists_biography", "personal_memoirs", "presidents_biography"
    ]
    bio_google = [
        'subject:"biography"', 'subject:"autobiography"', 'subject:"memoir"',
        'inauthor:"Walter Isaacson"', 'inauthor:"Ron Chernow"', 'inauthor:"David McCullough"',
        'inauthor:"Robert Caro"', 'inauthor:"Ashlee Vance"', 'inauthor:"Michelle Obama"',
        'inauthor:"Trevor Noah"', 'inauthor:"Tara Westover"', 'inauthor:"Jeanette Walls"',
        'inauthor:"Anne Frank"', 'inauthor:"Nelson Mandela"', 'inauthor:"Steve Jobs"'
    ]
    embed_genre_dataset("Biography", 2000, bio_subjects, bio_google)

    # 3. Young Adult (2000 books)
    ya_subjects = [
        "young_adult_fiction", "ya_fantasy", "ya_dystopian", "ya_romance",
        "teen_fiction", "coming_of_age", "high_school_fiction", "young_adult_literature"
    ]
    ya_google = [
        'subject:"young adult fiction"', 'subject:"teen fiction"', 'subject:"ya fantasy"',
        'inauthor:"Suzanne Collins"', 'inauthor:"John Green"', 'inauthor:"Rick Riordan"',
        'inauthor:"Veronica Roth"', 'inauthor:"Cassandra Clare"', 'inauthor:"Sarah J. Maas"',
        'inauthor:"Angie Thomas"', 'inauthor:"Jenny Han"', 'inauthor:"Rainbow Rowell"',
        'inauthor:"Becky Albertalli"', 'inauthor:"Karen M. McManus"', 'inauthor:"Holly Black"'
    ]
    embed_genre_dataset("Young Adult", 2000, ya_subjects, ya_google)

    print("\n==================================================")
    print(f"ALL INGESTION COMPLETE! Total ChromaDB collection size: {books_collection.count()}")
    print("==================================================")

if __name__ == "__main__":
    run()
