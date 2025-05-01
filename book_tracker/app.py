from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from book_tracker.models.book_model import Book
from book_tracker.models.user_model import Users
from book_tracker.models.shelf_model import Shelf
from book_tracker.utils.google_books_api import search_books
from book_tracker.db import db

import os

load_dotenv()

def create_app():
    """Create a Flask application with the specified configuration.

    Args:
        config_class (Config): The configuration class to use.

    Returns:
        Flask app: The configured Flask application.

    """
    app = Flask(__name__)
    app.config.from_object('book_tracker.config')
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///booktracker.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret_key")
    
    # Initialize database
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.filter_by(username=user_id).first()
    
    @login_manager.unauthorized_handler
    def unauthorized():
        return make_response(jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401)
    
    shelf_model = Shelf

    @app.route("/healthcheck", methods=["GET"])
    def healthcheck():
        """Health check route to verify the service is running.

        Returns:
            JSON response indicating the health status of the service.

        """
        return jsonify({"status": "ok"}), 200

    @app.route("/", methods=["GET"])
    def home():
        """Home route to verify the service path.

        Returns:
            JSON response indicating the correct service connection.

        """
        return jsonify({
            "message": "Welcome to the Book Tracker API!",
            "routes": {
                "healthcheck": "/healthcheck [GET]",
                "create_user": "/create-user [PUT]",
                "login": "/login [POST]",
                "logout": "/logout [POST]",
                "change_password": "/change-password [POST]",
                "search_books": "/search?query=... [GET]"
            }
        }), 200
    
    ##########################################################
    # User Management
    ##########################################################

    @app.route("/create-user", methods=["PUT"])
    def create_user():
        """Register a new user account.

        Expected JSON Input:
            - username (str): The desired username.
            - password (str): The desired password.

        Returns:
            JSON response indicating the success of the user creation.

        Raises:
            400 error if the username or password is missing.
            500 error if there is an issue creating the user in the database.
        """
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return jsonify({"error": "Missing username or password"}), 400
        try:
            Users.create_user(username, password)
            return jsonify({"status": "success", "message": "Account created successfully"}), 201
        except ValueError as e:
            return jsonify({"status": "error", "error": str(e)}), 400
        


    @app.route("/login", methods=["POST"])
    def login():
        """Authenticate a user and log them in.

        Expected JSON Input:
            - username (str): The username of the user.
            - password (str): The password of the user.

        Returns:
            JSON response indicating the success of the login attempt.

        Raises:
            401 error if the username or password is incorrect.
        """
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        try:
            if Users.check_password(username, password):
                user = Users.query.filter_by(username=username).first()
                login_user(user)
                return jsonify({"status": "success", "message": "Login successful"}), 200
            else:
                return jsonify({"status": "error", "error": "Invalid credentials"}), 401
        except ValueError as e:
            return jsonify({"status": "error", "error": str(e)}), 401

    @app.route("/logout", methods=["POST"])
    @login_required
    def logout():
        """Log out the current user.

        Returns:
            JSON response indicating the success of the logout operation.

        """
        logout_user()
        return jsonify({"status": "success", "message": "Logged out successfully"}), 200

    @app.route("/change-password", methods=["POST"])
    @login_required
    def change_password():
        """Change the password for the current user.

        Expected JSON Input:
            - new_password (str): The new password to set.

        Returns:
            JSON response indicating the success of the password change.

        Raises:
            400 error if the new password is not provided.
            500 error if there is an issue updating the password in the database.
        """
        data = request.get_json()
        new_password = data.get("new_password")
        if not new_password:
            return jsonify({"status": "error", "error": "New password required"}), 400
        try:
            Users.update_password(current_user.username, new_password)
            return jsonify({"status": "success", "message": "Password updated successfully"}), 200
        except ValueError as e:
            return jsonify({"status": "error", "error": str(e)}), 400
        
  

    @app.route("/reset-users", methods=["DELETE"])
    def reset_users():
        """Recreate the users table to delete all users.

        Returns:
            JSON response indicating the success of recreating the Users table.

        Raises:
            500 error if there is an issue recreating the Users table.
        """
        try:
            Users.query.delete()
            db.session.commit()
            return jsonify({"status": "success"}), 200
        except Exception as e:
            return jsonify({"status": "error", "error": str(e)}), 500


    

    ##########################################################
    # Books
    ##########################################################

    @app.route("/search", methods=["GET"])
    def search_books_route():
        """Queries Books through path to test service connection.

        Returns:
            JSON response indicating the success of recreating the Songs table.

        Raises:
            500 error if there is an issue recreating the Songs table.
        """
        query = request.args.get("query")
        if not query:
            return jsonify({"error": "Missing query parameter"}), 400
        try:
            books = search_books(query)
            return jsonify({"books": books}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/reset-books", methods=["DELETE"])
    def reset_books():
        """Recreate the books table to delete books.

        Returns:
            JSON response indicating the success of recreating the Books table.

        Raises:
            500 error if there is an issue recreating the Books table.
        """
        try:
            Book.query.delete()
            db.session.commit()
            return jsonify({"status": "success"}), 200
        except Exception as e:
            return jsonify({"status": "error", "error": str(e)}), 500

    @app.route("/create-book", methods=["POST"])
    @login_required
    def create_book():
        """Route to add a new book to the catalog.

        Expected JSON Input:
            - title (str): The book's title.
            - authors (str): The authors of the book.
            - description (str): The book's description (optional).
            - isbn (int): The isbn of the book (optional).
            - thumbnail (str): The book cover (optional).
            - shelf (str): Which shelf the book is in (default is WANT_TO_READ)

        Returns:
            JSON response indicating the success of the song addition.

        Raises:
            400 error if input validation fails.
            500 error if there is an issue adding the song to the playlist.

        """
        data = request.get_json()
        try:
            book = Book(
                title=data.get("title"),
                authors=data.get("authors"),
                isbn=data.get("isbn"),
                shelf=data.get("shelf")
            )
            db.session.add(book)
            db.session.commit()
            return jsonify({"status": "success", "id": book.id}), 201
        except Exception as e:
            return jsonify({"status": "error", "error": str(e)}), 400

    return app

if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).resolve().parent))
    app = create_app()
    app.run(debug=True)



