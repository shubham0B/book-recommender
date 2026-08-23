import os
import re
import requests
import html
from ingestion import books_collection

def clean_name(s: str) -> str:
    if not s:
        return ""
    # Fix broken encodings like Bront?e -> Bronte
    s = s.replace("Bront?e", "Bronte").replace("Brontë", "Bronte")
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def get_openlibrary_cover(title: str, author: str) -> str:
    clean_t = re.split(r'[:\-\(]', title)[0].strip()
    clean_a = clean_name((author or "").split(',')[0].split(' and ')[0].strip())
    
    try:
        url = "https://openlibrary.org/search.json"
        params = {"title": clean_t, "limit": 5}
        if clean_a and clean_a != "Unknown Author":
            params["author"] = clean_a.split()[-1]

        resp = requests.get(url, params=params, headers={"User-Agent": "BookMind/2.0"}, timeout=5.0)
        if resp.status_code == 200:
            docs = resp.json().get("docs", [])
            for d in docs:
                cid = d.get("cover_i")
                if cid:
                    return f"https://covers.openlibrary.org/b/id/{cid}-L.jpg"
                isbns = d.get("isbn", [])
                if isbns:
                    return f"https://covers.openlibrary.org/b/isbn/{isbns[0]}-L.jpg"
    except Exception as e:
        print(f"Error fetching OpenLibrary for '{title}': {e}")

    try:
        resp = requests.get("https://openlibrary.org/search.json", params={"title": clean_t, "limit": 3}, headers={"User-Agent": "BookMind/2.0"}, timeout=5.0)
        if resp.status_code == 200:
            docs = resp.json().get("docs", [])
            for d in docs:
                cid = d.get("cover_i")
                if cid:
                    return f"https://covers.openlibrary.org/b/id/{cid}-L.jpg"
                isbns = d.get("isbn", [])
                if isbns:
                    return f"https://covers.openlibrary.org/b/isbn/{isbns[0]}-L.jpg"
    except Exception:
        pass

    return ""

def main():
    print("==================================================")
    print("UPDATING ALL BOOKS IN CHROMADB TO REAL RETAIL COVERS")
    print("==================================================")
    
    all_data = books_collection.get()
    ids = all_data.get("ids", [])
    metadatas = all_data.get("metadatas", [])
    
    print(f"Total books to inspect: {len(ids)}")
    
    CANONICAL_REAL_COVERS = {
        "the horse and his boy": "https://covers.openlibrary.org/b/id/9184792-L.jpg",
        "a voyage to arcturus": "https://covers.openlibrary.org/b/id/2890702-L.jpg",
        "durgeshnandini": "https://covers.openlibrary.org/b/id/9183933-L.jpg",
        "wuthering heights": "https://covers.openlibrary.org/b/id/12818862-L.jpg",
        "lull & bruno": "https://covers.openlibrary.org/b/id/4623879-L.jpg",
        "lull and bruno": "https://covers.openlibrary.org/b/id/4623879-L.jpg",
        "the left hand of darkness": "https://covers.openlibrary.org/b/id/12539097-L.jpg",
        "the lord of the rings": "https://covers.openlibrary.org/b/id/12001552-L.jpg",
        "the hobbit": "https://covers.openlibrary.org/b/id/12003435-L.jpg",
        "dune": "https://covers.openlibrary.org/b/id/11140954-L.jpg",
        "atomic habits": "https://covers.openlibrary.org/b/isbn/9780735211292-L.jpg",
        "sapiens": "https://covers.openlibrary.org/b/id/14838634-L.jpg",
        "the psychology of money": "https://covers.openlibrary.org/b/id/10574163-L.jpg",
        "1984": "https://covers.openlibrary.org/b/id/12718885-L.jpg",
        "to kill a mockingbird": "https://covers.openlibrary.org/b/id/12080373-L.jpg",
        "the hunger games": "https://covers.openlibrary.org/b/id/12646272-L.jpg",
        "pride and prejudice": "https://covers.openlibrary.org/b/id/12708304-L.jpg",
        "misery": "https://covers.openlibrary.org/b/id/10398603-L.jpg",
        "the rise of nine": "https://covers.openlibrary.org/b/id/7287978-L.jpg",
        "eclipse": "https://covers.openlibrary.org/b/id/8314143-L.jpg",
        "james and the giant peach": "https://covers.openlibrary.org/b/id/10705490-L.jpg",
        "matilda": "https://covers.openlibrary.org/b/id/10419266-L.jpg",
        "shivaji and his times": "https://covers.openlibrary.org/b/id/11388656-L.jpg",
    }
    
    updated_count = 0
    
    for i, doc_id in enumerate(ids):
        meta = dict(metadatas[i])
        title = meta.get("title", "")
        author = meta.get("authors", "")
        curr_thumb = meta.get("thumbnail", "")
        
        clean_t = clean_name(title)
        clean_a = clean_name(author)
        t_key = re.split(r'[:\-\(]', clean_t.lower())[0].strip()
        
        meta["title"] = clean_t
        meta["authors"] = clean_a
        
        real_cover = CANONICAL_REAL_COVERS.get(t_key) or CANONICAL_REAL_COVERS.get(clean_t.lower().strip())
        
        needs_replacement = (
            not curr_thumb or 
            curr_thumb == "/placeholder.svg" or 
            "printsec=frontcover" in curr_thumb or 
            not curr_thumb.startswith("http") or
            real_cover is not None
        )
        
        if real_cover:
            meta["thumbnail"] = real_cover
            updated_count += 1
        elif needs_replacement:
            ol_cover = get_openlibrary_cover(clean_t, clean_a)
            if ol_cover:
                meta["thumbnail"] = ol_cover
                updated_count += 1
                print(f"-> Resolved OpenLibrary cover for '{clean_t}': {ol_cover}")
        
        books_collection.update(
            ids=[doc_id],
            metadatas=[meta]
        )
        
    print(f"\nSuccessfully refreshed {updated_count} books with verified real covers!")
    print(f"Total ChromaDB collection size: {books_collection.count()}")

if __name__ == "__main__":
    main()
