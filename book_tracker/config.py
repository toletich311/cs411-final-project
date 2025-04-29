import os
# --- Flask app configs ---

class ProductionConfig:
    SQLALCHEMY_DATABASE_URI = "sqlite:///booktracker.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")

class TestingConfig:
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True
    SECRET_KEY = "testing_secret_key"
    
GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"
GOOGLE_BOOKS_API_KEY = os.getenv("AIzaSyA0MpRk5vMryEYtXigzPs5phCRgsj2DzKo")