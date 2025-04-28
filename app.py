from flask import Flask
from book_tracker.db import db

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    
    db.init_app(app)

    @app.route("/healthcheck")
    def healthcheck():
        return {"status": "ok"}, 200

    return app

if __name__ == "__main__":
    create_app().run()

