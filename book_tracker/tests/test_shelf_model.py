import unittest
from unittest.mock import patch
from book_tracker.models.book_model import Book
from book_tracker.models.shelf_model import Shelf, ShelfCategory

class TestShelf(unittest.TestCase):

    def setUp(self):
        """Test setting up the 3 book shelves, and creating 2 different book objects"""
        self.shelf = Shelf()
        self.book1 = Book(title="The Hobbit", authors=["J.R.R. Tolkien"], description="Adventure fantasy")
        self.book2 = Book(title="Dune", authors=["Frank Herbert"], description="Sci-fi epic")

    def test_add_and_get_book(self):
        """Test adding a book to a shelf, and retrieving this book making sure it retrieves the book object from the shelf"""
        added = self.shelf.add_book(ShelfCategory.WANT_TO_READ, self.book1)
        self.assertEqual(added.id, 1)
        retrieved = self.shelf.get_book(1)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.title, "The Hobbit")

    def test_update_book(self):
        """Test updating a book, in this case changing the description and title and making sure the changes have been made"""
        self.shelf.add_book(ShelfCategory.FINISHED, self.book1)
        updated = Book(title="The Hobbit: Updated", authors=["J.R.R. Tolkien"], description="Updated desc")
        result = self.shelf.update_book(1, updated)
        self.assertEqual(result.title, "The Hobbit: Updated")

    def test_delete_book(self):
        """Test deleting a book, and then making sure that the shelf no longer contains this book"""
        self.shelf.add_book(ShelfCategory.CURRENTLY_READING, self.book2)
        deleted = self.shelf.delete_book(1)
        self.assertTrue(deleted)
        self.assertIsNone(self.shelf.get_book(1))

    def test_search_books_local(self):
        """Test adding books to the shelf, then searching the books by a keyword, in this case dune, and finding matches of the search"""
        self.shelf.add_book(ShelfCategory.WANT_TO_READ, self.book1)
        self.shelf.add_book(ShelfCategory.FINISHED, self.book2)
        results = self.shelf.search_books_local("dune")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Dune")

    @patch("book_tracker.models.shelf_model.search_books")
    def test_import_from_google(self, mock_search):
        """Test importing books from google books api, and adding them to the shelf"""
        mock_search.return_value = [
            {
                "title": "Mock Book A",
                "authors": ["Author A"],
                "description": "Desc A"
            },
            {
                "title": "Mock Book B",
                "authors": ["Author B"],
                "description": "Desc B"
            }
        ]
        books = self.shelf.import_from_google(ShelfCategory.WANT_TO_READ, "test query")
        self.assertEqual(len(books), 2)
        self.assertEqual(books[0].title, "Mock Book A")
        self.assertEqual(len(self.shelf.get_shelf(ShelfCategory.WANT_TO_READ)), 2)

if __name__ == '__main__':
    unittest.main()
