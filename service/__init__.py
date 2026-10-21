"""Flask application factory for the Customer Accounts microservice."""
import os

from flask import Flask
from flask_cors import CORS
from flask_talisman import Talisman

from service.models import db


def create_app(test_config=None):
    """Create and initialize the application."""
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///accounts.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        # Set TALISMAN_FORCE_HTTPS=false only for local HTTP development.
        TALISMAN_FORCE_HTTPS=os.getenv("TALISMAN_FORCE_HTTPS", "true").lower() == "true",
        # Comma-separated browser origins; set CORS_ALLOWED_ORIGINS in deployments.
        CORS_ALLOWED_ORIGINS=os.getenv(
            "CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
        ),
    )
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    allowed_origins = [
        origin.strip()
        for origin in app.config["CORS_ALLOWED_ORIGINS"].split(",")
        if origin.strip()
    ]
    CORS(
        app,
        resources={r"/accounts.*": {"origins": allowed_origins}},
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type"],
    )
    Talisman(
        app,
        force_https=app.config["TALISMAN_FORCE_HTTPS"] and not app.testing,
        content_security_policy={"default-src": "'self'"},
        frame_options="DENY",
    )

    from service.routes import accounts  # pylint: disable=import-outside-toplevel
    app.register_blueprint(accounts)
    with app.app_context():
        db.create_all()
    return app


app = create_app()
