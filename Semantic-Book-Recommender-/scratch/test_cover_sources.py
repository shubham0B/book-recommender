import requests

def test_sources(isbn, title, author):
    print("==================================================", flush=True)
    print(f"Testing for: '{title}' by '{author}' (ISBN: {isbn})", flush=True)
    
    # 1. Open Library by ISBN
    if isbn:
        ol_isbn_url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg?default=false"
        try:
            r = requests.get(ol_isbn_url, timeout=4)
            print(f"  [1] OpenLibrary ISBN ({ol_isbn_url}): Status {r.status_code}, Length {len(r.content)} bytes", flush=True)
        except Exception as e:
            print(f"  [1] OpenLibrary ISBN error: {e}", flush=True)

    # 2. Google Books Content direct image by ISBN (does NOT use API key quota)
    if isbn:
        gb_img_url = f"https://books.google.com/books/content?vid=ISBN{isbn}&printsec=frontcover&img=1&zoom=1"
        try:
            r = requests.get(gb_img_url, timeout=4)
            print(f"  [2] Google Content CDN ({gb_img_url}): Status {r.status_code}, Length {len(r.content)} bytes, ContentType: {r.headers.get('content-type')}", flush=True)
        except Exception as e:
            print(f"  [2] Google Content CDN error: {e}", flush=True)

test_sources('9780544003415', 'The Lord of the Rings', 'J.R.R. Tolkien')
test_sources('9780441172719', 'Dune', 'Frank Herbert')
test_sources('9780451524935', '1984', 'George Orwell')
test_sources('9780735211292', 'Atomic Habits', 'James Clear')
