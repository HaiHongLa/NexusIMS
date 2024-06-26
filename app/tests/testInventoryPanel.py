import unittest
import csv, json
from app import app, db
from models.component import Component
from models.inventory import ProductInventory, ComponentInventory
from models.product import Product
from models.productionFacility import ProductionFacility
from populateDb import parseFloat, normalizeString
from faker import Faker
from random import randint, sample


class TestInventoryChanges(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.app = app.test_client()
        faker = Faker()
        with app.app_context():
            db.create_all()

            with open("../sampleData/laptops.csv", "r", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                next(reader)
                # Manufacturer,Model Name,Category,Screen Size,Screen,CPU,RAM, Storage,GPU,Operating System,Operating System Version,Weight,Price (Euros)
                for i in range(20):
                    row = next(reader)
                    price = parseFloat(row[12]) * 1.07
                    if price != -1:
                        product = Product(
                            brand=row[0],
                            model=normalizeString(row[1]),
                            category=row[2],
                            price=price,
                            available=True,
                        )
                        db.session.add(product)
                db.session.commit()

            # Create components
            with open("../sampleData/sampleComponentData.csv", "r") as csvfile:
                reader = csv.reader(csvfile)
                next(reader)
                for i in range(20):
                    row = next(reader)
                    # ,brand_name,decription,ratings,prices,category
                    price = parseFloat(row[4])
                    if price != -1:
                        component = Component(
                            name=row[2],
                            brand=row[1],
                            price=price,
                            category=row[5],
                        )
                        db.session.add(component)
                db.session.commit()

            # Generate fake ProductionFacility objects and save them to the database
            with open("../sampleData/locations.csv") as csvfile:
                reader = csv.reader(csvfile)
                next(reader)
                # Street Address,City,State,Zipcode,Latitude,Longitude
                for row in reader:
                    facility = ProductionFacility(
                        name=f"{row[1]} Location",
                        contactInfo=faker.phone_number(),
                        streetAddress=row[0],
                        city=row[1],
                        stateProvinceRegion=row[2],
                        postalCode=row[3],
                        country="USA",
                        latitude=float(row[4]),
                        longitude=float(row[5]),
                    )
                    db.session.add(facility)
                db.session.commit()

            # Create inventory entries
            productIds = [product.id for product in Product.query.all()]
            facilities = ProductionFacility.query.all()

            for pf in facilities:
                selectedProducts = sample(productIds, 10)
                for i in selectedProducts:
                    entry = ProductInventory(
                        productId=i,
                        count=randint(20, 200),
                        productionFacilityId=pf.id,
                        lastUpdatedByUserId=1,
                    )
                    db.session.add(entry)
            db.session.commit()

            # Create component inventory entries
            componentIds = [c.id for c in Component.query.all()]
            for pf in facilities:
                selectedComps = sample(componentIds, 10)
                for i in selectedComps:
                    entry = ComponentInventory(
                        componentId=i,
                        count=randint(20, 200),
                        productionFacilityId=pf.id,
                        lastUpdatedByUserId=1,
                    )
                    db.session.add(entry)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def testSaveChangesSuccess(self):
        # Prepare request data
        changes_list = [
            {"type": "product", "entryId": 1, "quantity": 15},
            {"type": "component", "entryId": 2, "quantity": 25},
        ]
        data = {"changesList": changes_list}

        # Make POST request to the endpoint
        response = self.app.post(
            "/save-changes", data=json.dumps(data), content_type="application/json"
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data["msg"], "Inventory updated successfully.")

        # Check if inventory counts are updated
        with app.app_context():
            updatedProductEntry = ProductInventory.query.filter_by(id=1).first()
            updatedComponentEntry = ComponentInventory.query.filter_by(id=2).first()
            self.assertEqual(updatedProductEntry.count, 15)
            self.assertEqual(updatedComponentEntry.count, 25)

    def test_saveInventoryChanges_invalid_entry_type(self):
        # Prepare request data with invalid entry type
        changesList = [{"type": "invalid_type", "entryId": 1, "quantity": 15}]
        data = {"changesList": changesList}

        # Make POST request to the endpoint
        response = self.app.post(
            "/save-changes", data=json.dumps(data), content_type="application/json"
        )

        responseData = json.loads(response.data)
        self.assertEqual("Errors occured on 1/1 updates.", responseData["msg"])
        self.assertIn("Invalid inventory entry type.", responseData["errors"])
