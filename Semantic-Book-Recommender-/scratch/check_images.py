import requests

def check_image(isbn):
    url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
    response = requests.get(url)
    print(f"ISBN {isbn}: length {len(response.content)}, status {response.status_code}")

check_image("9780735211292") # Atomic Habits
check_image("9780857197689") # Psychology of Money (known working)
check_image("9780743273565") # The Great Gatsby
check_image("9780061120084") # To Kill a Mockingbird (known working)
