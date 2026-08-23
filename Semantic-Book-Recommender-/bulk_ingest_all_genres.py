import os
import time
import requests
from typing import List, Dict, Any
from ingestion import (
    books_collection,
    ingestion_service,
    get_embedding_model,
    build_semantic_text,
    make_dedup_key,
    resolve_authentic_cover
)

# Comprehensive list of rich genre queries and seminal search terms
BULK_QUERIES = [
    # Top Genres
    ("Fiction", "bestselling modern fiction novels"),
    ("Nonfiction", "popular general nonfiction books"),
    ("Fantasy", "epic fantasy and high fantasy books"),
    ("Science Fiction", "best science fiction novels space opera"),
    ("Mystery", "mystery detective thriller crime novels"),
    ("Thriller", "psychological thriller suspense novels"),
    ("Horror", "supernatural horror and gothic horror novels"),
    ("Romance", "contemporary romance and historical romance novels"),
    ("Self Development", "personal growth habits productivity self help books"),
    ("Psychology", "behavioral psychology cognitive science human mind books"),
    ("Philosophy", "classic philosophy stoicism ethics existentialism books"),
    ("History", "world history civilizations revolutions wars history books"),
    ("Biography", "biographies memoirs historical figures innovators"),
    ("Young Adult", "young adult dystopian fantasy coming of age books"),
    ("Children's Fiction", "children's classic literature adventure illustrated stories"),
    
    # Evergreen / Bestseller Collections
    ("Fiction", "award winning classic literature"),
    ("Science Fiction", "dystopian hard science fiction masterworks"),
    ("Fantasy", "mythology magical realism urban fantasy novels"),
    ("Self Development", "finance mindset discipline leadership success books")
]

def run_bulk_ingestion(books_per_query: int = 25):
    print("==================================================================")
    print("      BOOKMIND BULK VECTOR INGESTION & EMBEDDING PIPELINE        ")
    print("==================================================================")
    
    initial_count = books_collection.count()
    print(f"Current ChromaDB collection size: {initial_count} books")
    
    total_added = 0
    total_queries = len(BULK_QUERIES)
    
    for idx, (genre, query_text) in enumerate(BULK_QUERIES, 1):
        print(f"\n[{idx}/{total_queries}] Ingesting: '{genre}' -> Query: '{query_text}'...")
        
        try:
            # Fetch and dynamically ingest books for this genre
            res = ingestion_service.ingest_books(
                query=query_text,
                count=books_per_query,
                genre_filter=genre
            )
            
            added = res.get("imported", 0)
            skipped = res.get("duplicates", 0)
            total_added += added
            print(f"  -> Added & Embedded: {added} new books | Skipped (Existing/Filtered): {skipped}")
            
        except Exception as e:
            print(f"  -> Error ingesting '{query_text}': {e}")
            
        # Brief pause to avoid Google Books API rate limits
        time.sleep(0.5)

    final_count = books_collection.count()
    print("\n==================================================================")
    print("               BULK INGESTION COMPLETE SUMMARY                    ")
    print("==================================================================")
    print(f"Initial books:   {initial_count}")
    print(f"New books added: {total_added}")
    print(f"Total Database:  {final_count} fully embedded books in ChromaDB")
    print("==================================================================")

if __name__ == "__main__":
    run_bulk_ingestion(books_per_query=25)
