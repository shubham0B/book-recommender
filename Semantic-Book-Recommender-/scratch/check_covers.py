import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import chromadb
from ingestion import books_collection, resolve_authentic_cover

print("Total books in collection:", books_collection.count())
sample = books_collection.get(limit=25)

print("\n--- SAMPLE 25 BOOKS IN CHROMADB ---")
for i, m in enumerate(sample['metadatas']):
    title = m.get('title', 'N/A')
    authors = m.get('authors', 'N/A')
    genre = m.get('genre', 'N/A')
    isbn_13 = m.get('isbn_13', '')
    isbn_10 = m.get('isbn_10', '')
    thumb = m.get('thumbnail', '')
    print(f"[{i+1}] Title: '{title}' | Author: '{authors}' | ISBN13: '{isbn_13}' | ISBN10: '{isbn_10}'")
    print(f"    Raw Thumb in DB: '{thumb}'")

print("\n--- TEST RESOLVE COVER FOR FIRST 5 ---")
for i, m in enumerate(sample['metadatas'][:5]):
    title = m.get('title', '')
    author = m.get('authors', '')
    raw_thumb = m.get('thumbnail', '')
    resolved = resolve_authentic_cover(title, author, m.get('isbn_13', ''), m.get('isbn_10', ''), raw_thumb)
    print(f"[{i+1}] '{title}' -> Resolved Cover: '{resolved}'")
