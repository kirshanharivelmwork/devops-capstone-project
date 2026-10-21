"""Flask application factory for the Customer Accounts microservice."""
import os

from flask import Flask
from flask_cors import CORS

from service.models import db


def create_app(test_config=None):
    """Create and initialize the application."""
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///accounts.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if test_config:
        app.config.update(test_config)
    db.init_app(app)
    CORS(app)
    from service.routes import accounts  # pylint: disable=import-outside-toplevel
    app.register_blueprint(accounts)
    with app.app_context():
        db.create_all()
    return app


app = create_app()
