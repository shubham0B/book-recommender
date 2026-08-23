import requests

def test_cover(q):
    print("-------------------------------------------------")
    print(f"Testing query: {q}")
    r = requests.get('https://www.googleapis.com/books/v1/volumes', params={'q': q, 'maxResults': 1}, timeout=5)
    print(f"  HTTP Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        items = data.get('items', [])
        print(f"  Items count: {len(items)}")
        if items:
            v = items[0].get('volumeInfo', {})
            images = v.get('imageLinks', {})
            print(f"  Title: {v.get('title')}")
            print(f"  Thumbnail: {images.get('thumbnail')}")
        else:
            print(f"  No items. TotalItems in resp: {data.get('totalItems', 0)}")
    else:
        print(f"  Response text: {r.text[:200]}")

test_cover('isbn:9780544003415')
test_cover('intitle:Dune inauthor:Herbert')
test_cover('intitle:1984 inauthor:Orwell')
test_cover('Popular Fiction Gary Hoppenstand')
