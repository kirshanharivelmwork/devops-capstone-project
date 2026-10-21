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
        # Leave HTTPS enforcement enabled in deployments; disable in local HTTP
        # development with TALISMAN_FORCE_HTTPS=false.
        TALISMAN_FORCE_HTTPS=os.getenv("TALISMAN_FORCE_HTTPS", "true").lower() == "true",
    )
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    CORS(app)
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
