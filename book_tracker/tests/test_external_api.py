import pytest
import requests

from book_tracker.utils import search_books

RANDOM_NUMBER = 0.42

@pytest.fixture
@pytest.fixture
def mock_google_books_api(mocker):
    """Mock the Google Books API requests.get call."""
    mock_response = mocker.Mock()
    # Set the .json() method return value
    mock_response.json.return_value = {
        "items": [
            {
                "id": "123",
                "volumeInfo": {
                    "title": "Test Book",
                    "authors": ["Test Author"],
                    "description": "Test Description",
                    "imageLinks": {
                        "thumbnail": "http://example.com/image.jpg"
                    }
                }
            }
        ]
    }
    mock_response.raise_for_status = mocker.Mock()  # Prevent errors
    mocker.patch("requests.get", return_value=mock_response)
    return mock_response

#### IMPLEMENT THESE -- ADD 3/4 TESTS
