"""Integration tests for the Customer Accounts REST API."""
import pytest

from service import create_app
from service.models import db


@pytest.fixture
def client():
    """Provide a fresh in-memory database for each test."""
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"})
    with app.test_client() as test_client:
        yield test_client
    with app.app_context():
        db.drop_all()
        db.session.remove()


def test_health(client):
    """The health endpoint is available."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "OK"


def test_create_read_list_update_delete(client):
    """A customer can be created, read, listed, updated, and deleted."""
    payload = {
        "name": "Alex Example",
        "email": "alex@example.org",
        "address": "123 Example Street",
    }
    response = client.post("/accounts", json=payload)
    assert response.status_code == 201
    account_id = response.json["id"]
    assert response.json["email"] == "alex@example.org"

    response = client.get(f"/accounts/{account_id}")
    assert response.status_code == 200
    assert response.json["name"] == "Alex Example"

    response = client.get("/accounts")
    assert response.status_code == 200
    assert len(response.json) == 1

    response = client.put(f"/accounts/{account_id}", json={"name": "Alex Updated"})
    assert response.status_code == 200
    assert response.json["name"] == "Alex Updated"

    response = client.delete(f"/accounts/{account_id}")
    assert response.status_code == 204
    assert client.get(f"/accounts/{account_id}").status_code == 404


def test_validation(client):
    """Invalid account payloads are rejected."""
    assert client.post("/accounts", json={}).status_code == 400
    assert client.post("/accounts", data="invalid").status_code == 400
    assert client.put("/accounts/999", json={}).status_code == 404
    assert client.delete("/accounts/999").status_code == 404
