import unittest
from unittest.mock import MagicMock
from app import app, db
from werkzeug.security import generate_password_hash
from models.user import User


# TODO camelCase
class testLoginLogout(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
            # Create a test user for use in the tests
            db.session.query(User).delete()
            test_user = User(
                username="valid_user",
                passwordHash=generate_password_hash("valid_password"),
                role=1,  # Set role as needed
                firstName="Test",
                lastName="User",
                phoneNumber="1234567890",
                email="test@example.com",
                title="Tester",
            )
            db.session.add(test_user)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.drop_all()

    def testValidLogin(self):
        # check for denial of access to authorized pages and redirection to login
        response = self.app.get("/admin/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(str(response.headers["location"]), "/login")

        # Simulate a POST request with valid credentials
        response = self.app.post(
            "/login",
            data={"username": "valid_user", "password": "valid_password"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.request.path), "/dashboard")

        # Ensure session contains the logged-in user
        with self.app as c:
            with c.session_transaction() as session:
                self.assertTrue(session["username"])

        # Check for access to authorized pages
        response = self.app.get("/admin", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.request.path), "/admin/")

    def testInvalidLogin(self):
        # Checks for failed login attempt before anything
        response = self.app.get("/admin", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.request.path), "/login")

        # Simulate a POST request with invalid credentials
        response = self.app.post(
            "/login",
            data={"username": "invalid_user", "password": "invalid_password"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.request.path), "/login")

        # Checks for failed access to restricted access page
        response = self.app.get("/admin", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.request.path), "/login")

    def testLoginGetRequest(self):
        # Simulate a GET request to the login page
        response = self.app.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.request.path), "/login")

    def testLogout(self):
        # Logs in a user and checks for access to admin page
        response = self.app.post(
            "/login", data={"username": "valid_user", "password": "valid_password"}
        )
        response = self.app.get("/admin", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.request.path), "/admin/")

        # Simulate a GET request to logout
        response = self.app.get("/logout", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.request.path), "/")

        # checks for restricted access to admin page
        response = self.app.get("/admin", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.request.path), "/login")

        # Ensure session doesn't contain the logged-in user anymore
        with self.app as c:
            with c.session_transaction() as session:
                self.assertNotIn("username", session)
