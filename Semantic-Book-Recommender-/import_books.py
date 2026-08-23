import os
import sys
import argparse

# Ensure path is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from ingestion import ingestion_service, GENRE_MAP, books_collection

def main():
    parser = argparse.ArgumentParser(description="BookMind Google Books Ingestion CLI")
    parser.add_argument("--genre", type=str, default=None, help="Target genre to import (e.g. Fantasy, Mystery, Science Fiction, Psychology)")
    parser.add_argument("--query", type=str, default=None, help="Custom search query (e.g. 'space opera', 'cognitive behavioral')")
    parser.add_argument("--count", type=int, default=20, help="Number of books to import (default: 20)")
    parser.add_argument("--all-genres", action="store_true", help="Import top books across all curated genres")

    args = parser.parse_args()

    print("==================================================")
    print("BOOKMIND GOOGLE BOOKS INGESTION CLI")
    print(f"Current ChromaDB Collection Size: {books_collection.count()} books")
    print("==================================================")

    if args.all_genres:
        genres = [
            "Psychology", "Science Fiction", "Fantasy", "Mystery", "Thriller",
            "Horror", "Romance", "Self Development", "History", "Philosophy",
            "Biography", "Young Adult"
        ]
        print(f"Importing {args.count} books for each of the {len(genres)} curated genres...")
        for g in genres:
            print(f"\n---> Ingesting genre: {g}")
            res = ingestion_service.ingest_books(query=g, count=args.count, genre_filter=g)
            print(f"Result for {g}: Imported {res['imported']} new books, {res['duplicates']} duplicates.")
    elif args.genre:
        res = ingestion_service.ingest_books(query=args.query or args.genre, count=args.count, genre_filter=args.genre)
        print(f"\nImport Summary:")
        print(f"  Status: {res['status']}")
        print(f"  New books imported: {res['imported']}")
        print(f"  Duplicates skipped: {res['duplicates']}")
        print(f"  Total books in ChromaDB: {res['total_books']}")
        if res.get('sample_imported'):
            print("  Sample imported titles:")
            for t in res['sample_imported']:
                print(f"    - {t}")
    elif args.query:
        res = ingestion_service.ingest_books(query=args.query, count=args.count, genre_filter=None)
        print(f"\nImport Summary for '{args.query}':")
        print(f"  Status: {res['status']}")
        print(f"  New books imported: {res['imported']}")
        print(f"  Duplicates skipped: {res['duplicates']}")
        print(f"  Total books in ChromaDB: {res['total_books']}")
        if res.get('sample_imported'):
            print("  Sample imported titles:")
            for t in res['sample_imported']:
                print(f"    - {t}")
    else:
        print("Please specify --genre, --query, or --all-genres.")
        print(f"Available genres: {', '.join(GENRE_MAP.keys())}")
        parser.print_help()

if __name__ == "__main__":
    main()
