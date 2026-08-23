import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import requests
from ingestion import books_collection

sample = books_collection.get(limit=10)
for i, m in enumerate(sample['metadatas']):
    title = m.get('title')
    isbn = m.get('isbn_13') or m.get('isbn_10') or ''
    if isbn:
        clean_isbn = isbn.replace('-', '').strip()
        gb_url = f"https://books.google.com/books/content?vid=ISBN{clean_isbn}&printsec=frontcover&img=1&zoom=1"
        try:
            r = requests.get(gb_url, timeout=3)
            print(f"[{i+1}] '{title}' (ISBN {clean_isbn}): Status {r.status_code}, Length {len(r.content)} bytes, Type: {r.headers.get('content-type')}", flush=True)
        except Exception as e:
            print(f"[{i+1}] '{title}': Error {e}", flush=True)
