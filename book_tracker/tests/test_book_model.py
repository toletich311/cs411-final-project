import time

import pytest

from book_tracker.db import db
from book_tracker.models.book_model import Book
from book_tracker.app import create_app
#from book_tracker.models.shelf_model import Shelf

# --- Fixtures ---
@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })
    return app

@pytest.fixture
def session(app):
    with app.app_context():
        yield db.session

@pytest.fixture
def book_harry(session):
    """Fixture for 'Harry Potter' book."""
    book = Book(title="Harry Potter", authors="J.K. Rowling")
    session.add(book)
    session.commit()
    return book

@pytest.fixture
def book_gatsby(session):
    """Fixture for 'The Great Gatsby' book."""
    book = Book(title="The Great Gatsby", authors="F. Scott Fitzgerald")
    session.add(book)
    session.commit()
    return book



# --- Validate Book ---

def test_validate_book_success():
    """Test that a valid book passes validation."""
    book = Book(title="Valid Title", authors="Valid Author")
    book.validate()  # Should not raise

def test_validate_book_missing_title():
    """Test that missing title raises a ValueError."""
    book = Book(title="", authors="Valid Author")
    with pytest.raises(ValueError, match="Title must be a non-empty string"):
        book.validate()

def test_validate_book_invalid_shelf():
    """Test that an invalid shelf raises a ValueError."""
    book = Book(title="Valid Title", authors="Valid Author", shelf="invalid_shelf")
    with pytest.raises(ValueError, match="Invalid shelf"):
        book.validate()

# --- Create Book ---

def test_create_book_success(session):
    # CLEANUP before starting
    existing = session.query(Book).filter_by(title="New Book", authors="New Author").first()
    if existing:
        session.delete(existing)
        session.commit()

    # Now create the book
    Book.create_book(title="New Book", authors="New Author")
    book = session.query(Book).filter_by(title="New Book", authors="New Author").first()
    assert book is not None
    assert book.title == "New Book"
    assert book.shelf == "want_to_read"

def test_create_book_duplicate(session, book_harry):
    """Test creating a duplicate book raises ValueError."""
    with pytest.raises(ValueError, match="already exists"):
        Book.create_book(title="Harry Potter", authors="J.K. Rowling")

# --- Get Book ---

def test_get_book_by_id(book_harry):
    """Test retrieving a book by ID."""
    fetched = Book.get_book_by_id(book_harry.id)
    assert fetched.title == "Harry Potter"

def test_get_book_by_id_not_found(app):
    """Test error when retrieving non-existent book by ID."""
    with app.app_context():
        with pytest.raises(ValueError, match="not found"):
            Book.get_book_by_id(999)


# --- Get Books By Shelf ---

def test_get_books_by_shelf(session, book_harry, book_gatsby):
    """Test retrieving books by shelf name."""
    books = Book.get_books_by_shelf("want_to_read")
    titles = [b.title for b in books]
    assert "Harry Potter" in titles
    assert "The Great Gatsby" in titles


def test_get_books_by_invalid_shelf(session):
    """Test retrieving books with a non-existent shelf returns empty list."""
    books = Book.get_books_by_shelf("nonexistent_shelf")
    assert books == []


# --- Delete Book ---

def test_delete_book(session, book_harry):
    """Test successfully deleting a book."""
    Book.delete_book(book_harry.id)
    assert session.get(Book, book_harry.id) is None   


def test_delete_book_not_found(app):
    """Test deleting a non-existent book raises ValueError."""
    with app.app_context():
        with pytest.raises(ValueError, match="not found"):
            Book.delete_book(999)



