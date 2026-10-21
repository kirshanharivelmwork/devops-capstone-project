"""REST routes for the Customer Accounts service."""
from datetime import date

from flask import Blueprint, jsonify, request

from service.models import Account, db

accounts = Blueprint("accounts", __name__)


@accounts.get("/")
def index():
    """Return the Account REST API reference metadata."""
    return jsonify({"name": "Account REST API Service", "version": "1.0"}), 200


@accounts.get("/health")
def health():
    """Provide a simple health check."""
    return jsonify({"status": "OK", "service": "Customer Accounts"}), 200


@accounts.post("/accounts")
def create_account():
    """Create a customer account."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "JSON object required"}), 400
    required = ("name", "email", "address")
    if any(not data.get(key) for key in required):
        return jsonify({"error": "name, email, and address are required"}), 400
    account = Account(
        name=data["name"],
        email=data["email"],
        address=data["address"],
        phone_number=data.get("phone_number"),
        date_joined=date.fromisoformat(data["date_joined"])
        if data.get("date_joined") else date.today(),
    )
    db.session.add(account)
    db.session.commit()
    return jsonify(account.serialize()), 201


@accounts.get("/accounts")
def list_accounts():
    """Return all customer accounts."""
    records = db.session.execute(db.select(Account).order_by(Account.id)).scalars()
    return jsonify([record.serialize() for record in records]), 200


@accounts.get("/accounts/<int:account_id>")
def read_account(account_id):
    """Return one customer account."""
    account = db.session.get(Account, account_id)
    if account is None:
        return jsonify({"error": "Account not found"}), 404
    return jsonify(account.serialize()), 200


@accounts.put("/accounts/<int:account_id>")
def update_account(account_id):
    """Update a customer account."""
    account = db.session.get(Account, account_id)
    if account is None:
        return jsonify({"error": "Account not found"}), 404
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "JSON object required"}), 400
    for field in ("name", "email", "address", "phone_number"):
        if field in data:
            setattr(account, field, data[field])
    if "date_joined" in data:
        account.date_joined = date.fromisoformat(data["date_joined"])
    db.session.commit()
    return jsonify(account.serialize()), 200


def _remove_account(account_id):
    """Delete an explicitly identified record, never the entire collection."""
    account = db.session.get(Account, account_id)
    if account is None:
        return jsonify({"error": "Account not found"}), 404
    db.session.delete(account)
    db.session.commit()
    return "", 204


@accounts.delete("/accounts/<int:account_id>")
def delete_account(account_id):
    """Delete an account using its usual resource URL."""
    return _remove_account(account_id)


@accounts.delete("/accounts")
def delete_account_collection_alias():
    """Accept the reference collection URL with an explicit JSON account ID."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or type(data.get("id")) is not int:
        return jsonify({"error": "Integer account id is required"}), 400
    return _remove_account(data["id"])
