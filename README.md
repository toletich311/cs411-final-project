# cs411-final-project

This is our repository for our CS411 Final project. 

Book Tracker is a RESTful API for managing a collection of books. Users can search for books via an external API, add books to their personal library, and track favorites. This project was built for Boston University’s CS411 final project and is containerized with Docker for consistent deployment.

Features
-Search for books using the Google Books API
-Add Books to one of your shelves
-Remove books from shelves
-etc. 
-Includes smoketests and unit tests

Setup
-Clone the repo
-Set up virtual environment (for local testing)
-Build the image
-Run the container
-Run Tests

API Endpoints
GET	/books	List all books
POST	/books	Add a new book
DELETE	/books/<id>	Remove a book
POST	/books/<id>/fav	Mark a book as favorite
GET	/search?q=...	Search via Google Books

