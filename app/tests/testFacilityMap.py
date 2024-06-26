import unittest, json
from app import app, db
from models.productionFacility import ProductionFacility


class TestFacility(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app = app.test_client()
        with app.app_context():
            db.drop_all()
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def testNoFacility(self):
        jsonData = self.app.get("/map-data").data
        actualMapData = json.loads(jsonData)
        expectedMapData = {"lat": [], "lon": [], "text": []}
        self.assertEqual(actualMapData, expectedMapData)

    def testGetMapData(self):
        with app.app_context():
            for i in range(3):
                f = ProductionFacility(
                    name=f"Facility {i}",
                    latitude=i * 10,
                    longitude=i * 20,
                )
                db.session.add(f)
            db.session.commit()

        jsonData = self.app.get("/map-data").data
        actualMapData = json.loads(jsonData)
        expectedMapData = {
            "lat": [0.0, 10.0, 20.0],
            "lon": [0.0, 20.0, 40.0],
            "text": ["Facility 0", "Facility 1", "Facility 2"],
        }
        self.assertEqual(actualMapData, expectedMapData)
