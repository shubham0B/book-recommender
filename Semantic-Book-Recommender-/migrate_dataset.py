import os
import sys
import json
import time
import pandas as pd
import numpy as np

# Ensure path is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from ingestion import (
    books_collection,
    chroma_client,
    get_embedding_model,
    classify_book_genres,
    make_dedup_key,
    build_semantic_text,
    normalize_string,
    COLLECTION_NAME
)

def run_migration(csv_path: str = None, max_books: int = 1500, batch_size: int = 100, reset: bool = True):
    """Migrate curated high-quality books from static CSV into ChromaDB vector store with exact ratings."""
    if not csv_path:
        csv_path = os.path.join(current_dir, "books_with_emotions.csv")
        if not os.path.exists(csv_path):
            csv_path = os.path.join(current_dir, "books_cleaned.csv")

    if not os.path.exists(csv_path):
        print(f"Error: CSV dataset not found at {csv_path}")
        return

    print(f"==================================================")
    print(f"STARTING STATIC DATASET MIGRATION TO CHROMADB")
    print(f"Source CSV: {csv_path}")
    print(f"==================================================")

    df = pd.read_csv(csv_path)
    print(f"Found {len(df)} total rows in CSV.")

    embedding_model = get_embedding_model()

    global books_collection
    if reset:
        print("Resetting ChromaDB collection for clean migration...")
        try:
            chroma_client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
        books_collection = chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

    existing_ids = set()
    existing_keys = set()

    records_to_insert = []
    skipped_dup = 0
    skipped_invalid = 0

    for idx, row in df.iterrows():
        title = normalize_string(str(row.get("title", "")))
        if not title or title.lower() == "unknown title" or len(title) < 2:
            skipped_invalid += 1
            continue

        raw_authors = str(row.get("authors", "Unknown Author"))
        authors_split = raw_authors.split(";")
        if len(authors_split) == 2:
            authors_str = f"{normalize_string(authors_split[0])} and {normalize_string(authors_split[1])}"
        elif len(authors_split) > 2:
            authors_str = f"{', '.join(normalize_string(a) for a in authors_split[:-1])}, and {normalize_string(authors_split[-1])}"
        else:
            authors_str = normalize_string(raw_authors)

        desc = str(row.get("description", ""))
        desc_clean = "" if desc.lower() == "nan" else normalize_string(desc)
        raw_cat = str(row.get("categories", ""))

        primary_genre, genres_list = classify_book_genres(raw_cat, authors_str, title)

        # Exact rating from Goodreads dataset
        rating_val = 4.0
        if pd.notna(row.get("average_rating")):
            try:
                r_num = float(row["average_rating"])
                if r_num > 0.5:
                    rating_val = round(r_num, 2)
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

        # Thumbnail
        thumb = str(row.get("thumbnail", "")).strip()
        if not thumb or thumb == "nan" or thumb == "cover-not-found.jpg" or "nophoto" in thumb:
            thumb = f"https://covers.openlibrary.org/b/isbn/{isbn_13 or isbn_10}-L.jpg" if (isbn_13 or isbn_10) else "/placeholder.svg"

        doc_id = f"local_{isbn_13 or idx}"
        dedup_key = make_dedup_key(title, authors_str)

        if doc_id in existing_ids or dedup_key in existing_keys:
            skipped_dup += 1
            continue
        if isbn_13 and isbn_13 in existing_keys:
            skipped_dup += 1
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
            "categories": raw_cat,
            "genre": primary_genre,
            "genres_json": json.dumps(genres_list),
            "publisher": "",
            "published_date": str(row.get("year_published", "")),
            "isbn_10": isbn_10,
            "isbn_13": isbn_13,
            "page_count": 0,
            "language": "en",
            "thumbnail": thumb,
            "preview_link": "",
            "info_link": f"https://openlibrary.org/isbn/{isbn_13}" if isbn_13 else f"https://openlibrary.org/search?title={title.replace(' ', '+')}",
            "source": "BookMind Library",
            "rating": rating_val,
            "dedup_key": dedup_key,
            "semantic_doc": semantic_doc,
            "created_at": int(time.time())
        }

        records_to_insert.append(book_item)
        if len(records_to_insert) >= max_books:
            break

    print(f"Prepared {len(records_to_insert)} unique books for embedding & ingestion. (Skipped: {skipped_dup} duplicates, {skipped_invalid} invalid).")

    if not records_to_insert:
        print("No new records to migrate.")
        return

    # Batch embedding and insertion into ChromaDB
    total = len(records_to_insert)
    inserted_count = 0

    for i in range(0, total, batch_size):
        batch = records_to_insert[i:i + batch_size]
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
        inserted_count += len(batch)
        print(f"Migrated batch {inserted_count}/{total} books to ChromaDB...")

    print(f"\n==================================================")
    print(f"MIGRATION COMPLETE! Total books in ChromaDB: {books_collection.count()}")
    print(f"==================================================")

if __name__ == "__main__":
    count_arg = 1500
    if len(sys.argv) > 1:
        try:
            count_arg = int(sys.argv[1])
        except Exception:
            pass
    run_migration(max_books=count_arg, reset=True)
