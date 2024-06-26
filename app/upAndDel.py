from random import choice
from faker import Faker

from app import app, db
from models.component import Component
from models.inventory import ProductInventory
from models.product import Product
from models.productionFacility import ProductionFacility
from models.user import User

faker = Faker()

with app.app_context():
    db.drop_all()
    db.create_all()
    db.session.query(User).delete()  # This deletes all users
    db.session.commit()

    # Update 10 fake products
    all_products = Product.query.all()
    for _ in range(10):
        # Randomly select a product to update
        product_to_update = choice(all_products)

        # Update some attributes of the product
        product_to_update.price = faker.random_number(digits=3)
        product_to_update.availability = faker.boolean(chance_of_getting_true=50)

    # Commit once after all updates
    db.session.commit()

    # delete some fake products
    all_products = Product.query.all()
    if all_products:  # Check if the list is not empty
        product_to_delete = choice(all_products)
        db.session.delete(product_to_delete)  # Delete the product from the database
        all_products.remove(product_to_delete)
    # Commit once after all updates
    db.session.commit()

    # Update 10 fake components
    all_components = Component.query.all()
    for _ in range(10):
        component_to_update = choice(all_components)
        component_to_update.price = faker.random_number(digits=3)
        component_to_update.availability = faker.boolean(chance_of_getting_true=50)
    db.session.commit()

    # Update 10 fake ProductionFacilities
    all_ProductionFacilities = ProductionFacility.query.all()
    for _ in range(10):
        ProductionFacility_to_update = choice(all_ProductionFacilities)
        ProductionFacility_to_update.contactInfo = faker.phone_number()
        ProductionFacility_to_update.availability = faker.boolean(
            chance_of_getting_true=50
        )
    db.session.commit()
