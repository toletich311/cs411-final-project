import pytest
import requests
from book_tracker.utils.google_books_api import search_books

@pytest.fixture
def mock_google_books_api(mocker):
    #patch google books api call
    #returns object replaced with mocker
    mock_response = mocker.Mock()
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
    mock_response.raise_for_status = mocker.Mock()
    mocker.patch("requests.get", return_value=mock_response)
    return mock_response


def test_search_books_success(mock_google_books_api):
    """Test successful response from Google Books API."""
    results = search_books("Test Query")

    assert isinstance(results, list)
    assert len(results) == 1
    book = results[0]
    assert book["id"] == "123"
    assert book["title"] == "Test Book"
    assert book["authors"] == "Test Author"
    assert book["description"] == "Test Description"
    assert book["thumbnail"] == "http://example.com/image.jpg"

def test_search_books_empty(mock_google_books_api):
    """Test when the API returns no items."""
    mock_google_books_api.json.return_value = {"items": []}
    results = search_books("Query with no results")
    assert results == []

def test_search_books_request_failure(mocker):
    """Test that request failures raise a RuntimeError."""
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("API error"))
    with pytest.raises(RuntimeError, match="Request to Google Books API failed: API error"):
        search_books("fail query")


def test_search_books_timeout(mocker):
    """Test that a timeout raises a RuntimeError."""
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)
    with pytest.raises(RuntimeError, match="Google Books API request timed out."):
        search_books("timeout query")
