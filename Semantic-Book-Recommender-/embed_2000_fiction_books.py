import os
import sys
import json
import time
import re
import pandas as pd
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from ingestion import (
    books_collection,
    get_embedding_model,
    classify_book_genres,
    make_dedup_key,
    build_semantic_text,
    normalize_string,
    is_bestseller_title
)

def embed_fiction_books(target_count: int = 2000, batch_size: int = 64):
    csv_path = os.path.join(current_dir, "books_with_emotions.csv")
    if not os.path.exists(csv_path):
        csv_path = os.path.join(current_dir, "books_cleaned.csv")
        
    print("==================================================")
    print(f"VECTOR EMBEDDING {target_count} FICTION BOOKS INTO CHROMADB")
    print(f"Source Dataset: {csv_path}")
    print("==================================================")

    df = pd.read_csv(csv_path)
    print(f"Total rows loaded: {len(df)}")

    embedding_model = get_embedding_model()

    # Get existing collection keys to prevent duplicates
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
        print(f"Notice on existing keys: {e}")
        existing_ids = set()
        existing_keys = set()

    print(f"Existing books in ChromaDB: {len(existing_ids)}")

    # Filter Fiction books
    fiction_candidates = []
    spam_patterns = [
        r'\bsummary\b', r'\banalysis of\b', r'\bworkbook\b', r'\bguidebook\b',
        r'\bstudy guide\b', r'\bcompanion to\b', r'\bkey takeaways\b',
        r'\bnotes on\b', r'\bjournal\b', r'\bnotebook\b', r'\bcalendar\b',
        r'\bplanner\b', r'\bcondensed version\b', r'\bunauthorized\b',
        r'\baction guide\b', r'\bquick read\b', r'\bcheat sheet\b',
        r'\bcatalogue of\b', r'\bwriter\'s market\b', r'\bwriters market\b',
        r'\breview of contemporary\b', r'\bliterature in the marketplace\b'
    ]

    for idx, row in df.iterrows():
        cat = str(row.get("simple_categories", ""))
        if cat != "Fiction":
            continue

        title = normalize_string(str(row.get("title", "")))
        if not title or len(title) < 2 or title.lower() == "unknown title":
            continue

        t_low = title.lower()
        if is_bestseller_title(title) or any(re.search(pat, t_low) for pat in spam_patterns):
            continue

        thumb = str(row.get("thumbnail", "")).strip()
        if not thumb or thumb == "nan" or not thumb.startswith("http") or "placeholder" in thumb or "cover-not-found" in thumb:
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

        primary_genre, genres_list = classify_book_genres(raw_cat, authors_str, title, fallback_genre="Fiction")

        # Rating
        rating_val = 4.2
        if pd.notna(row.get("average_rating")):
            try:
                r_num = float(row["average_rating"])
                if r_num > 0.5:
                    rating_val = round(r_num, 1)
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
                clean_isbn10 = str(row["isbn10"]).strip()
                if clean_isbn10 and clean_isbn10 != "nan":
                    isbn_10 = clean_isbn10
            except Exception:
                pass

        ratings_count = 0
        if pd.notna(row.get("ratings_count")):
            try:
                ratings_count = int(float(row["ratings_count"]))
            except Exception:
                pass

        doc_id = f"fic_{isbn_13 or idx}"
        dedup_key = make_dedup_key(title, authors_str)

        if doc_id in existing_ids or dedup_key in existing_keys:
            continue
        if isbn_13 and isbn_13 in existing_keys:
            continue

        existing_ids.add(doc_id)
        existing_keys.add(dedup_key)
        if isbn_13:
            existing_keys.add(isbn_13)

        desc_words = desc_clean.split()
        trunc_desc = " ".join(desc_words[:35]) + ("..." if len(desc_words) > 35 else "")
        semantic_doc = build_semantic_text(title, authors_str, primary_genre, raw_cat, desc_clean)

        book_item = {
            "id": doc_id,
            "google_books_id": "",
            "title": title,
            "authors": authors_str,
            "description": trunc_desc,
            "full_description": desc_clean[:1000],
            "categories": raw_cat if raw_cat != "nan" else "Fiction",
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
            "rating": rating_val,
            "ratings_count": ratings_count,
            "dedup_key": dedup_key,
            "semantic_doc": semantic_doc,
            "created_at": int(time.time())
        }

        fiction_candidates.append(book_item)
        if len(fiction_candidates) >= target_count:
            break

    print(f"Selected {len(fiction_candidates)} distinct high-quality Fiction books for vector embedding.")

    if not fiction_candidates:
        print("All target Fiction books are already embedded.")
        return

    # Batch embedding and storing in ChromaDB
    total = len(fiction_candidates)
    inserted_count = 0
    t0 = time.time()

    for i in range(0, total, batch_size):
        batch = fiction_candidates[i:i + batch_size]
        semantic_texts = [r["semantic_doc"] for r in batch]
        
        # Dense vector embeddings via SentenceTransformer (384 dimensions)
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
        print(f"[{inserted_count}/{total}] Embedded and stored in ChromaDB ({rate:.1f} books/sec)...")

    final_count = books_collection.count()
    print("\n==================================================")
    print(f"SUCCESS: {inserted_count} Fiction books vector embedded!")
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
    embed_fiction_books(target_count=count)
