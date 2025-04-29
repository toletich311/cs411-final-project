import logging
from typing import List

from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError

from book_tracker.db import db
from book_tracker.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)


class Book(db.Model):
    """Represents a Book tracked by a user.

    This model maps to the 'books' table in the database and stores information
    such as title, author(s), description, ISBN, cover image, and shelf status.
    """

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    authors = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    isbn = db.Column(db.String(20), nullable=True)
    thumbnail = db.Column(db.String(255), nullable=True) #may delete
    shelf = db.Column(db.String(50), nullable=False, default="want_to_read") # I want to make shelf struct 

    def __init__(self, title: str, authors: str, description: str = None,
                 isbn: str = None, thumbnail: str = None, shelf: str = "want_to_read"):
        """Initialize a new Book instance.

        Args:
            title (str): The title of the book.
            authors (str): The authors of the book.
            description (str, optional): A brief description of the book.
            isbn (str, optional): The ISBN number of the book.
            thumbnail (str, optional): A URL to the book's thumbnail image.
            shelf (str, optional): The shelf where the book is categorized. Defaults to 'want_to_read'.
        """
        self.title = title
        self.authors = authors
        self.description = description
        self.isbn = isbn
        self.thumbnail = thumbnail
        self.shelf = shelf


    def validate(self) -> None:
        """
        Validates the book instance before committing to the database.

        Raises:
            ValueError: If any required fields are invalid or if shelf value is not recognized.
        """
        if not self.title or not isinstance(self.title, str):
            raise ValueError("Title must be a non-empty string.")
        if not self.authors or not isinstance(self.authors, str):
            raise ValueError("Authors must be a non-empty string.")
        if self.shelf not in {"want_to_read", "currently_reading", "finished"}:
            raise ValueError(f"Invalid shelf '{self.shelf}'.")
        
    @classmethod
    def create_book(cls, title: str, authors: str, description: str = None,
                    isbn: str = None, thumbnail: str = None, shelf: str = "want_to_read") -> None:
        """
        Create and persist a new Book instance.

        Args:
            title (str): The title of the book.
            authors (str): The authors of the book.
            description (str, optional): A brief description.
            isbn (str, optional): ISBN number.
            thumbnail (str, optional): URL to the thumbnail.
            shelf (str, optional): Shelf category (default: 'want_to_read').

        Raises:
            ValueError: If the book already exists or if validation fails.
            SQLAlchemyError: If a database error occurs during creation.
        """
        logger.info(f"Received request to create book: {title} by {authors}")

        try:
            book = Book(
                title=title.strip(),
                authors=authors.strip(),
                description=description,
                isbn=isbn,
                thumbnail=thumbnail,
                shelf=shelf
            )
            book.validate()
        except ValueError as e:
            logger.warning(f"Validation failed: {e}")
            raise

        try:
            existing = Book.query.filter_by(title=title.strip(), authors=authors.strip()).first()
            if existing:
                logger.error(f"Book already exists: {title} by {authors}")
                raise ValueError(f"Book '{title}' by '{authors}' already exists.")

            db.session.add(book)
            db.session.commit()
            logger.info(f"Book successfully added: {title} by {authors}")

        except IntegrityError:
            logger.error(f"Book already exists: {title} by {authors}")
            db.session.rollback()
            raise ValueError(f"Book '{title}' by '{authors}' already exists.")

        except SQLAlchemyError as e:
            logger.error(f"Database error while creating book: {e}")
            db.session.rollback()
            raise

    @classmethod
    def get_book_by_id(cls, book_id: int) -> "Book":
        """
        Retrieve a book by its ID.

        Args:
            book_id (int): The ID of the book.

        Returns:
            Book: The retrieved book instance.

        Raises:
            ValueError: If no book with the given ID is found.
            SQLAlchemyError: If a database error occurs.
        """
        logger.info(f"Attempting to retrieve book with ID {book_id}")

        try:
            book = db.session.get(cls, book_id)
            if not book:
                logger.warning(f"Book with ID {book_id} not found")
                raise ValueError(f"Book with ID {book_id} not found")
            return book

        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving book: {e}")
            raise

    @classmethod
    def get_books_by_shelf(cls, shelf: str) -> List["Book"]:
        """
        Retrieve all books by shelf name.

        Args:
            shelf (str): The shelf category to filter by.

        Returns:
            List[Book]: List of books on the specified shelf.

        Raises:
            SQLAlchemyError: If a database error occurs.
        """
        logger.info(f"Attempting to retrieve books on shelf '{shelf}'")

        try:
            books = cls.query.filter_by(shelf=shelf).all()
            return books
        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving books by shelf: {e}")
            raise
    

    @classmethod
    def delete_book(cls, book_id: int) -> None:
        """
        Delete a book by its ID.

        Args:
            book_id (int): The ID of the book to delete.

        Raises:
            ValueError: If the book with the given ID is not found.
            SQLAlchemyError: If a database error occurs.
        """
        logger.info(f"Received request to delete book with ID {book_id}")

        try:
            book = cls.get_book_by_id(book_id)
            db.session.delete(book)
            db.session.commit()
            logger.info(f"Successfully deleted book with ID {book_id}")

        except SQLAlchemyError as e:
            logger.error(f"Database error while deleting book with ID {book_id}: {e}")
            db.session.rollback()
            raise

    def move_shelf(self, new_shelf: str) -> None:
        """
        Move a book to a new shelf.

        Args:
            new_shelf (str): The new shelf category.

        Raises:
            ValueError: If the new shelf value is invalid.
            SQLAlchemyError: If a database error occurs.
        """
        logger.info(f"Moving book '{self.title}' from '{self.shelf}' to '{new_shelf}'")

        if new_shelf not in {"want_to_read", "currently_reading", "finished"}:
            raise ValueError(f"Invalid new shelf '{new_shelf}'.")

        try:
            self.shelf = new_shelf
            db.session.commit()
            logger.info(f"Book '{self.title}' moved to shelf '{new_shelf}'")
        except SQLAlchemyError as e:
            logger.error(f"Database error while moving book shelf: {e}")
            db.session.rollback()
            raise


