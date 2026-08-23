import requests

def is_valid_cover_url(url: str) -> bool:
    if not url or not url.startswith("http") or "/placeholder.svg" in url or "cover-not-found" in url:
        return False
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, stream=True, timeout=3.0)
        if r.status_code != 200:
            return False
            
        content_type = r.headers.get("Content-Type", "")
        if "image" not in content_type:
            return False
            
        content_length = r.headers.get("Content-Length")
        if content_length and int(content_length) < 1000: # 1x1 gif is ~43 bytes
            return False
            
        # if Content-Length is missing or we just want to be sure:
        chunk = next(r.iter_content(chunk_size=2048), b"")
        if len(chunk) < 500: # a real book cover is way more than 500 bytes
            return False
            
        return True
    except Exception as e:
        print(f"Error checking {url}: {e}")
        return False

# Test OpenLibrary missing cover
print("OpenLibrary missing:", is_valid_cover_url("https://covers.openlibrary.org/b/isbn/9783161484100-L.jpg"))

# Test Google Books real cover
print("Google Books real:", is_valid_cover_url("https://books.google.com/books/content?vid=ISBN9780441172719&printsec=frontcover&img=1&zoom=1"))

# Test Backend API real cover (this returns redirect to Google Books or OpenLibrary)
print("Backend dynamic API:", is_valid_cover_url("http://localhost:8000/api/books/cover?title=Dune&author=Frank+Herbert&isbn=9780441172719"))
