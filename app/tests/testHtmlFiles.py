"""
This design a unit test that cover the frontend files
Routes that are related are:
- '/login' : User login page.
- '/infoModal' : Endpoint for displaying an information modal.
- '/signup' : User signup page.
- '/information' : Information page.
"""

import unittest
from werkzeug.security import generate_password_hash
from bs4 import BeautifulSoup
from models.user import User
from app import (
    app,
    db,
)


class TestWebApp(unittest.TestCase):
    """
    Tester for frontend Html using bs4 modules
    method:
        login as a proper user and then extract the html file form the webpage
        then with bs4 create a beautiful soup that contains all the components of the webpage in a readable form
        Unit test is going to test certain properties of the html file
    """

    def setUp(self):
        # Initialize the test client and database
        self.app = app.test_client()
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        # Initialize the database and create test data
        with app.app_context():
            db.drop_all()
            db.create_all()
            test_user = User(
                username="valid_user",
                passwordHash=generate_password_hash("valid_password"),
            )
            db.session.add(test_user)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.drop_all()  # Drop all tables after tests to ensure a clean state

    def test_login_content(self):
        response = self.app.get("/login")
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.data, "html.parser")
        login_header = soup.find("h2").get_text()
        self.assertEqual(login_header, "Login", "Login header not found or incorrect")

    def test_signup_content(self):
        response = self.app.get("/signup")
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.data, "html.parser")
        signup_header = soup.find("h2").get_text()
        self.assertEqual(
            signup_header, "Sign Up", "Sign Up header not found or incorrect"
        )

    def test_information_content(self):
        response = self.app.get("/information")
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.data, "html.parser")
        intro_text_exists = soup.find("div", class_="intro") is not None
        self.assertTrue(intro_text_exists, "Intro text not found")

        start_button = soup.find("button", class_="start-btn")
        self.assertIsNotNone(start_button, "Start button not found")
        self.assertEqual(
            start_button.get("onclick"),
            "location.href='/login'",
            "Start button redirect incorrect",
        )
