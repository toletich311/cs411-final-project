from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from book_tracker.models.book_model import Book
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

    @app.route("/healthcheck", methods=["GET"])
    def healthcheck():
        return jsonify({"status": "ok"}), 200


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
    create_app().run()



