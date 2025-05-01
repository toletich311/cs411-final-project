import requests

from book_tracker.config import GOOGLE_BOOKS_API_URL, GOOGLE_BOOKS_API_KEY

def search_books(query):
    params = {
        "q": query,
        "key": GOOGLE_BOOKS_API_KEY,
        "maxResults": 10
    }

    try:
        response = requests.get(GOOGLE_BOOKS_API_URL, params=params)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise RuntimeError("Google Books API request timed out.")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Request to Google Books API failed: {e}")

    data = response.json()
    books = []

    for item in data.get("items", []):
        volume_info = item.get("volumeInfo", {})
        books.append({
            "id": item.get("id"),
            "title": volume_info.get("title", ""),
            "authors": ", ".join(volume_info.get("authors", [])),
            "description": volume_info.get("description", ""),
            "thumbnail": volume_info.get("imageLinks", {}).get("thumbnail", "")
        })

    return books