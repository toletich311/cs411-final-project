import logging
import math
import os
import time
from enum import Enum
from typing import Dict, List, Optional

from book_tracker.models.book_model import Book
from book_tracker.utils.logger import configure_logger
from book_tracker.utils.google_books_api import search_books

logger = logging.getLogger(__name__)
configure_logger(logger)

class ShelfCategory(Enum):
    WANT_TO_READ = "want_to_read"
    CURRENTLY_READING = "currently_reading"
    FINISHED = "finished"

class Shelf:
    """
    In-memory shelf manager with categorized books.
    """

    def __init__(self):
        """
        Initializes 3 book shelves, want to read, currently reading, and finished. 
        Users are able to add books and move them around these shelves
        """
        self.shelves: Dict[ShelfCategory, List[Book]] = {
            ShelfCategory.WANT_TO_READ: [],
            ShelfCategory.CURRENTLY_READING: [],
            ShelfCategory.FINISHED: []
        }
        self.next_id = 1
        logger.info("Shelf initialized with 3 empty categories.")

    def add_book(self, category: ShelfCategory, book: Book) -> Book:
        """
        Adds a new book to a particular shelf

        Args:
            category (ShelfCategory): Type of Shelf.
            book (Book): The book to be added to the shelf.
        """
        if self._book_exists(category, book):
            logger.warning(f"Book '{book.title}' already exists in shelf '{category.value}'. Skipping.")
            return book
        book.id = self.next_id
        self.next_id += 1
        self.shelves[category].append(book)
        logger.info(f"Book added: {book.title} (id={book.id}) to shelf '{category.value}'")
        return book

    def get_book(self, book_id: int) -> Optional[Book]:
        """
        Retrieves a book by iterating through shelves

        Args:
            book_id (int): ID of the specified books
        """
        for shelf in self.shelves.values():
            for book in shelf:
                if book.id == book_id:
                    logger.info(f"Book retrieved: {book.title} (id={book.id})")
                    return book
        logger.warning(f"Book with id={book_id} not found.")
        return None

    def get_all_books(self) -> List[Book]:
        """
        Returns a list of all books from all shelves
        """
        all_books = [book for shelf in self.shelves.values() for book in shelf]
        logger.info(f"Retrieved all books from all shelves: {len(all_books)} total.")
        return all_books

    def get_shelf(self, category: ShelfCategory) -> List[Book]:
        """
        Retrieves a certain shelf

        Args:
            category (ShelfCategory): certain shelf
        """
        return self.shelves.get(category, [])

    def update_book(self, book_id: int, updated: Book) -> Optional[Book]:
        """
        Replaces a certain book in the shelf by updating it with new book.

        Args:
            book_id (int): id of the old book
            updated (Book): book object of the new updated book
        """
        for shelf in self.shelves.values():
            for i, book in enumerate(shelf):
                if book.id == book_id:
                    updated.id = book_id
                    shelf[i] = updated
                    logger.info(f"Book updated: id={book_id} → {updated.title}")
                    return updated
        logger.warning(f"Book with id={book_id} not found for update.")
        return None

    def delete_book(self, book_id: int) -> bool:
        """
        Removes a book from the shelves.

        Args:
            book_id (int): id of the old book
        """
        for shelf_category, shelf in self.shelves.items():
            for i, book in enumerate(shelf):
                if book.id == book_id:
                    del shelf[i]
                    logger.info(f"Book deleted: id={book_id} from shelf '{shelf_category.value}'")
                    return True
        logger.warning(f"Book with id={book_id} not found for deletion.")
        return False

    def import_from_google(self, category: ShelfCategory, query: str) -> List[Book]:
        """
        Search Google Books API and add results to the given category shelf.

        Args:
            category (ShelfCategory): certain shelf
            query (str): the query sent to book API
        """
        logger.info(f"Importing books into '{category.value}' from Google API with query: '{query}'")
        results = search_books(query)
        imported_books = []
        for item in results:
            book = Book(
                title=item.get("title", "Untitled"),
                authors=item.get("authors", ["Unknown"]),
                description=item.get("description", "")
            )
            added = self.add_book(category, book)
            imported_books.append(added)
        logger.info(f"Imported {len(imported_books)} books into shelf '{category.value}'")
        return imported_books

    def _book_exists(self, category: ShelfCategory, new_book: Book) -> bool:
        """
        Given a specified shelf checks if the book exists on that shelf

        Args:
            category (ShelfCategory): certain shelf
            new_book (Book): the book to see if exists on the shelf
        """
        for book in self.shelves[category]:
            if book.title == new_book.title and book.authors == new_book.authors:
                return True
        return False

    def search_books_local(self, keyword: str) -> List[Book]:
        """
        given a keyword will look for a certain book that matches the keyword

        Args:
            keyword: (str): the keyword to look for
        """
        keyword_lower = keyword.lower()
        results = [
            book for book in self.get_all_books()
            if keyword_lower in book.title.lower() or keyword_lower in book.description.lower()
        ]
        logger.info(f"Searched all shelves for '{keyword}', found {len(results)} result(s).")
        return results
