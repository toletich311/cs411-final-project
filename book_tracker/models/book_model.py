import logging
from typing import List

from sqlalchemy.exc import IntegrityError

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
        """Initialize a new Book instance."""
        self.title = title
        self.authors = authors
        self.description = description
        self.isbn = isbn
        self.thumbnail = thumbnail
        self.shelf = shelf

    #add methods here

