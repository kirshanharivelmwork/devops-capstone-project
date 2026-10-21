"""Integration tests for the Customer Accounts REST API."""
import unittest

from service import create_app
from service.models import db


class AccountsRouteTests(unittest.TestCase):
    """Exercise the Accounts service with an isolated test database."""

    def setUp(self):
        """Create a fresh in-memory database for each test."""
        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
        })
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up database tables and the active session."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_health(self):
        """The health endpoint is available."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "OK")

    def test_create_read_list_update_delete(self):
        """A customer can be created, read, listed, updated, and deleted."""
        payload = {
            "name": "Alex Example",
            "email": "alex@example.org",
            "address": "123 Example Street",
        }
        response = self.client.post("/accounts", json=payload)
        self.assertEqual(response.status_code, 201)
        account_id = response.json["id"]
        self.assertEqual(response.json["email"], "alex@example.org")

        response = self.client.get(f"/accounts/{account_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], "Alex Example")

        response = self.client.get("/accounts")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)

        response = self.client.put(f"/accounts/{account_id}", json={"name": "Alex Updated"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], "Alex Updated")

        response = self.client.delete(f"/accounts/{account_id}")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.client.get(f"/accounts/{account_id}").status_code, 404)

    def test_validation(self):
        """Invalid account payloads are rejected."""
        self.assertEqual(self.client.post("/accounts", json={}).status_code, 400)
        self.assertEqual(self.client.post("/accounts", data="invalid").status_code, 400)
        self.assertEqual(self.client.put("/accounts/999", json={}).status_code, 404)
        self.assertEqual(self.client.delete("/accounts/999").status_code, 404)
