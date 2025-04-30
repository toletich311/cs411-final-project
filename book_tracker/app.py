from flask import Flask, jsonify, make_response, Response, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from book_tracker.models.book_model import Book
from book_tracker.models.user_model import Users
from book_tracker.models.shelf_model import Shelf
from book_tracker.utils.google_books_api import search_books
from book_tracker.db import db
from dotenv import load_dotenv

import os

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object('book_tracker.config')
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///booktracker.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret_key")
    
    db.init_app(app)

    #if empty create maybe delete??
    with app.app_context():
        db.create_all()

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
        return jsonify({"status": "ok"}), 200

    @app.route("/", methods=["GET"])
    def home():
        return jsonify({
            "message": "Welcome to the Book Tracker API!",
            "routes": {
                "healthcheck": "/healthcheck [GET]",
                "create_account": "/create-account [PUT]",
                "login": "/login [POST]",
                "logout": "/logout [POST]",
                "update_password": "/update-password [POST]",
                "search_books": "/search?query=... [GET]"
            }
        }), 200
    ##########################################################
    #
    # User Managment 
    #
    ##########################################################
    @app.route("/create-account", methods=["PUT"])
    def create_account():
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return jsonify({"error": "Missing username or password"}), 400
        try:
            Users.create_user(username, password)
            return jsonify({"message": "Account created successfully"}), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        
    @app.route("/login", methods=["POST"])
    def login():
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        try:
            if Users.check_password(username, password):
                user = Users.query.filter_by(username=username).first()
                login_user(user)
                return jsonify({"message": "Login successful"}), 200
            else:
                return jsonify({"error": "Invalid credentials"}), 401
        except ValueError as e:
            return jsonify({"error": str(e)}), 401
        
    @app.route("/logout", methods=["POST"])
    @login_required
    def logout():
        logout_user()
        return jsonify({"message": "Logged out successfully"}), 200
    
    @app.route("/update-password", methods=["POST"])
    @login_required
    def update_password():
        data = request.get_json()
        new_password = data.get("new_password")
        if not new_password:
            return jsonify({"error": "New password required"}), 400
        try:
            Users.update_password(current_user.username, new_password)
            return jsonify({"message": "Password updated successfully"}), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    

    ##########################################################
    #
    # Books
    #
    ##########################################################

    @app.route("/search", methods=["GET"])
    def search_books_route():
        query = request.args.get("query")
        if not query:
            return jsonify({"error": "Missing query parameter"}), 400

        try:
            books = search_books(query)
            return jsonify({"books": books}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return app

if __name__ == "__main__":
    import sys
    from pathlib import Path
    # Add the parent directory to sys.path to resolve `book_tracker` imports
    sys.path.append(str(Path(__file__).resolve().parent))

    app = create_app()
    app.run(debug=True)



