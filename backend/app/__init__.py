import os

from flask import Flask
from flask_cors import CORS

from config import Config
from app.extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    CORS(app, origins=app.config["FRONTEND_ORIGINS"])
    db.init_app(app)

    from app import models  # noqa: F401
    from app.routes import candidates_bp, documents_bp, public_bp

    app.register_blueprint(candidates_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(public_bp)

    @app.cli.command("create-db")
    def create_db():
        """Create all tables from the current models."""
        db.create_all()
        print("Tables created.")

    @app.cli.command("drop-db")
    def drop_db():
        """Drop all tables."""
        db.drop_all()
        print("Tables dropped.")

    return app
