from random import randint, sample
from faker import Faker
import csv

from app import app, db
from models.component import Component
from models.inventory import ProductInventory, ComponentInventory
from models.product import Product
from models.productionFacility import ProductionFacility
from models.user import User

faker = Faker()


def parseFloat(inputValue):
    if isinstance(inputValue, float):
        return inputValue
    try:
        # If input is not already a float, try to convert it
        number_str = str(inputValue).replace(",", "")
        return float(number_str)
    except ValueError:
        # Return -1 if conversion fails
        return -1


def normalizeString(inputString):
    try:
        # Try to decode the string using UTF-8 encoding
        normalizedString = inputString.encode("latin-1").decode("utf-8")
        return normalizedString
    except Exception as e:
        # If decoding fails, return the original string
        return ""


if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()

        # create 10 fake users
        titles = ["Corporate Manager", "Inventory Manager", "IT Manager", "Employee"]
        for i in range(20):
            user = User(
                username=f"user{i}",
                firstName=faker.first_name(),
                lastName=faker.last_name(),
                phoneNumber=faker.phone_number(),
                email=faker.email(),
                title=faker.random_element(elements=titles),
            )
            user.setPassword(f"password{i}")
            db.session.add(user)
        db.session.commit()

        # Create products
        with open("../sampleData/laptops.csv", "r", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            # Manufacturer,Model Name,Category,Screen Size,Screen,CPU,RAM, Storage,GPU,Operating System,Operating System Version,Weight,Price (Euros)
            for row in reader:
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
            db.create_all()
            for row in reader:
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
            selectedProducts = sample(productIds, 50)
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
            selectedComps = sample(componentIds, 50)
            for i in selectedComps:
                entry = ComponentInventory(
                    componentId=i,
                    count=randint(20, 200),
                    productionFacilityId=pf.id,
                    lastUpdatedByUserId=1,
                )
                db.session.add(entry)
        db.session.commit()
