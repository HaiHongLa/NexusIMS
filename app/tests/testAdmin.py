import unittest
from app import app, admin, db


class TestAdmin(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.drop_all()

    def authenticate(self):
        with self.app.session_transaction() as session:
            session["username"] = "user1"

    def testAdminIndexLoginRequired(self):
        # Check that admin index page is login protected
        response = self.app.get("/admin", follow_redirects=True)

        # Check that admin request gets redirected to /login
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(str(response.request.path), "/admin")

    def testViewsCreated(self):
        expectedAdminViews = [
            "/admin",
            "/admin/user",
            "/admin/product",
            "/admin/component",
            "/admin/productionfacility",
            "/admin/databasetransaction",
        ]

        actualAdminViews = [v.url for v in admin._views]
        for view in expectedAdminViews:
            self.assertIn(view, actualAdminViews)

        self.authenticate()
        adminUrls = [view.url for view in admin._views]
        for url in adminUrls:
            response = self.app.get(url, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(url, response.request.url)
