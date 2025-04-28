import requests

from book_tracker.config import GOOGLE_BOOKS_API_URL, GOOGLE_BOOKS_API_KEY

def search_books(query):
    """Search for books using the Google Books API."""
    params = {
        'q': query,
        'maxResults': 10,
    }
    if GOOGLE_BOOKS_API_KEY:
        params['key'] = GOOGLE_BOOKS_API_KEY

    response = requests.get(GOOGLE_BOOKS_API_URL, params=params)
    response.raise_for_status()
    data = response.json()

    books = []
    for item in data.get('items', []):
        volume_info = item.get('volumeInfo', {})
        books.append({
            'id': item.get('id'),
            'title': volume_info.get('title', 'No Title'),
            'authors': volume_info.get('authors', []),
            'description': volume_info.get('description', 'No Description'),
            'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail', '')
        })

    return books
