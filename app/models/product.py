"""
Database model for products.

This module defines the database model for products. It includes fields for various 
attributes of products and event listeners for recording database transactions after 
insert and update operations.
"""

from sqlalchemy import event
from extensions import db
from models.dbUtils import BaseModel
from models.transaction import DatabaseTransaction
from datetime import datetime


class Product(db.Model, BaseModel):
    """
    Represents a product in the database.

    Attributes:
        id (int): The unique identifier for the product.
        brand (str): The brand of the product.
        model (str): The model of the product.
        category (str): The category to which the product belongs.
        price (float): The price of the product.
        specs (str): The specifications of the product.
        notes (str): Additional notes about the product.
        image_url (str): The URL to the image of the product.
        available (bool): Indicates whether the product is available or not.

    Methods:
        __repr__: Returns a string representation of the product.
    """

    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    brand = db.Column(db.String(100), nullable=True)
    model = db.Column(db.String(100), nullable=True)
    category = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    specs = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(256), nullable=True)
    available = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        """
        Returns a string representation of the product.

        Returns:
            str: A string representation of the product.
        """
        return "<Product %r>" % self.name


@event.listens_for(Product, "after_insert")
def after_product_insert(mapper, connection, target):
    """
    Event listener function triggered after a product is inserted into the database.

    Args:
        mapper: The mapper object.
        connection: The connection object.
        target: The newly inserted product object.
    """
    changes_description = (
        f"Product inserted with "
        f"Model: {target.model}, Category: {target.category}, Price: {target.price}"
    )
    transaction = DatabaseTransaction(
        objectId=target.id,
        tableName="product",
        operation="insert",
        changes=changes_description,
        timestamp=datetime.now(),
    )
    db.session.add(transaction)


@event.listens_for(Product, "after_update")
def after_product_update(mapper, connection, target):
    """
    Event listener function triggered after a product is updated in the database.

    Args:
        mapper: The mapper object.
        connection: The connection object.
        target: The updated product object.
    """
    state = db.inspect(target)
    changes = {}

    for attr in state.attrs:
        # The key property on this object gives us the name of the attribute as a string (for example, 'name').
        # True: this is a boolean flag that tells get_history() whether or not to return the 'unchanged' portion of the history.
        # hist: The History object contains three lists representing the changes to the attribute: added, unchanged, and deleted.
        hist = state.get_history(attr.key, True)
        if hist.has_changes():
            if hist.has_changes():
                changes[attr.key] = {
                    # hist.deleted: This list contains the value(s) that were present before the update operation and have been replaced or deleted
                    # hist.added: This list contains the new value(s) that have been set during the update operation
                    "old": hist.deleted[0] if hist.deleted else None,
                    "new": hist.added[0] if hist.added else None,
                }

    if changes:
        change_description = "; ".join(
            f'{key} changed from {vals["old"]} to {vals["new"]}'
            for key, vals in changes.items()
        )
        transaction = DatabaseTransaction(
            objectId=target.id,
            tableName="product",
            operation="update",
            changes=change_description,
            timestamp=datetime.now(),
        )
    db.session.add(transaction)


@event.listens_for(Product, "before_delete")
def beforeProductDelete(mapper, connection, target):
    """
    Event listener function triggered before a product is deleted from the database.

    Args:
        mapper: The mapper object.
        connection: The connection object.
        target: The product object to be deleted.
    """
    state = db.inspect(target)
    change_description = []
    for attr in state.attrs:
        value = getattr(target, attr.key)
        if value is not None:
            change_description.append(f"{attr.key} was '{value}'")
        change_description_str = "; ".join(change_description)
    transaction = DatabaseTransaction(
        objectId=target.id,
        tableName="product",
        operation="delete",
        changes=f"Deleted product {change_description_str}",
        timestamp=datetime.now(),
    )
    db.session.add(transaction)
