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

    def test_security_headers(self):
        """Talisman attaches browser security headers to API responses."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")
        self.assertIn("default-src 'self'", response.headers["Content-Security-Policy"])

    def test_cors_allowed_origin(self):
        """Configured browser origins receive the CORS allowance."""
        response = self.client.get(
            "/accounts", headers={"Origin": "http://localhost:3000"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Access-Control-Allow-Origin"),
            "http://localhost:3000",
        )

    def test_cors_blocked_origin(self):
        """Unknown browser origins are not granted CORS access."""
        response = self.client.get(
            "/accounts", headers={"Origin": "https://untrusted.example"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Access-Control-Allow-Origin", response.headers)

    def test_cors_preflight(self):
        """CORS preflight permits an allowed POST with JSON content."""
        response = self.client.options(
            "/accounts",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Access-Control-Allow-Origin"),
            "http://localhost:3000",
        )
        self.assertIn("POST", response.headers["Access-Control-Allow-Methods"])
        self.assertIn("content-type", response.headers["Access-Control-Allow-Headers"].lower())

    def test_api_root_metadata(self):
        """The root route identifies the Account REST API Service."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"name": "Account REST API Service", "version": "1.0"})

    def test_empty_accounts_list(self):
        """A new service starts with an empty account listing."""
        response = self.client.get("/accounts")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    def test_create_returns_id(self):
        """A created account contains an integer account identifier."""
        response = self.client.post(
            "/accounts", json={"name": "Pat", "email": "pat@example.org", "address": "1 Main St"}
        )
        self.assertEqual(response.status_code, 201)
        self.assertIsInstance(response.json["id"], int)

    def test_create_defaults_join_date(self):
        """An account receives a valid default join date."""
        response = self.client.post(
            "/accounts", json={"name": "Pat", "email": "pat@example.org", "address": "1 Main St"}
        )
        self.assertRegex(response.json["date_joined"], r"^\\d{4}-\\d{2}-\\d{2}$")

    def test_read_unknown_account(self):
        """An unknown account returns 404 on GET."""
        self.assertEqual(self.client.get("/accounts/999").status_code, 404)

    def test_update_unknown_account(self):
        """An unknown account returns 404 on PUT."""
        self.assertEqual(self.client.put("/accounts/999", json={"name": "Pat"}).status_code, 404)

    def test_delete_unknown_account(self):
        """An unknown account returns 404 on DELETE."""
        self.assertEqual(self.client.delete("/accounts/999").status_code, 404)

    def test_create_missing_name(self):
        """A CREATE request must include a name."""
        response = self.client.post(
            "/accounts", json={"email": "pat@example.org", "address": "1 Main St"}
        )
        self.assertEqual(response.status_code, 400)

    def test_create_missing_email(self):
        """A CREATE request must include an email."""
        response = self.client.post("/accounts", json={"name": "Pat", "address": "1 Main St"})
        self.assertEqual(response.status_code, 400)

    def test_create_missing_address(self):
        """A CREATE request must include an address."""
        response = self.client.post(
            "/accounts", json={"name": "Pat", "email": "pat@example.org"}
        )
        self.assertEqual(response.status_code, 400)

    def test_create_invalid_json(self):
        """Non-JSON requests are rejected."""
        self.assertEqual(self.client.post("/accounts", data="broken").status_code, 400)

    def test_update_invalid_json(self):
        """Non-JSON update requests are rejected."""
        response = self.client.post(
            "/accounts", json={"name": "Pat", "email": "pat@example.org", "address": "1 Main St"}
        )
        account_id = response.json["id"]
        self.assertEqual(self.client.put(f"/accounts/{account_id}", data="bad").status_code, 400)

    def test_update_name_persists(self):
        """Updated customer names remain readable."""
        response = self.client.post(
            "/accounts", json={"name": "Pat", "email": "pat@example.org", "address": "1 Main St"}
        )
        account_id = response.json["id"]
        self.assertEqual(
            self.client.put(f"/accounts/{account_id}", json={"name": "New"}).status_code, 200
        )
        self.assertEqual(self.client.get(f"/accounts/{account_id}").json["name"], "New")

    def test_update_phone_persists(self):
        """Updated phone details remain readable."""
        response = self.client.post(
            "/accounts", json={"name": "Pat", "email": "pat@example.org", "address": "1 Main St"}
        )
        account_id = response.json["id"]
        self.client.put(f"/accounts/{account_id}", json={"phone_number": "555-0123"})
        self.assertEqual(
            self.client.get(f"/accounts/{account_id}").json["phone_number"], "555-0123"
        )

    def test_delete_collection_requires_id(self):
        """DELETE /accounts never deletes an entire collection by accident."""
        self.assertEqual(self.client.delete("/accounts", json={}).status_code, 400)

    def test_delete_collection_by_id(self):
        """DELETE /accounts with an explicit ID deletes the selected account."""
        response = self.client.post(
            "/accounts", json={"name": "Pat", "email": "pat@example.org", "address": "1 Main St"}
        )
        account_id = response.json["id"]
        self.assertEqual(self.client.delete("/accounts", json={"id": account_id}).status_code, 204)
        self.assertEqual(self.client.get(f"/accounts/{account_id}").status_code, 404)

    def test_it_should_return_a_cors_header(self):
        """It should return a CORS header"""
        response = self.client.get(
            "/accounts", headers={"Origin": "http://localhost:3000"}
        )
        self.assertEqual(
            response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3000"
        )

    def test_it_should_return_security_headers(self):
        """It should return security headers"""
        response = self.client.get("/health")
        self.assertIn("Content-Security-Policy", response.headers)
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")
