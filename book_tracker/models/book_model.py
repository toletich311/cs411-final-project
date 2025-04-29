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

