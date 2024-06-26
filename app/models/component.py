"""
Database model for PC components.

This module defines the database model for PC components such as CPU, GPU, etc. 
It includes fields for various attributes of components and event listeners for 
recording database transactions after insert and update operations.
"""

from extensions import db
from models.dbUtils import BaseModel
from sqlalchemy import event
from models.transaction import DatabaseTransaction
from datetime import datetime


class Component(db.Model, BaseModel):
    """
    Represents a PC component in the database.

    Attributes:
        id (int): The unique identifier for the component.
        name (str): The name of the component.
        category (str): The category of the component (e.g., CPU, GPU).
        brand (str): The brand of the component.
        model (str): The model of the component.
        price (float): The price of the component.
        specs (str): Specifications of the component.

    Methods:
        __repr__: Returns a string representation of the component.
    """

    __tablename__ = "components"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256), nullable=True)
    category = db.Column(db.String(100), nullable=True)
    brand = db.Column(db.String(100), nullable=True)
    model = db.Column(db.String(100), nullable=True)
    price = db.Column(db.Float, nullable=True)
    specs = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"{self.brand} {self.name} {self.model}"


@event.listens_for(Component, "after_insert")
def after_component_insert(mapper, connection, target):

    transaction = DatabaseTransaction(
        objectId=target.id,
        tableName="component",
        operation="insert",
        changes=f"Component created with Name: {target.name},"
        + " Brand: {target.brand}, Price: {target.price}",
        timestamp=datetime.now(),
    )
    db.session.add(transaction)


@event.listens_for(Component, "after_update")
def after_component_update(mapper, connection, target):
    state = db.inspect(target)
    changes = {}
    for attr in state.attrs:
        hist = state.get_history(attr.key, True)
        if hist.has_changes():
            if hist.has_changes():
                changes[attr.key] = {
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
            tableName="component",
            operation="update",
            changes=f"Component {change_description}",
            timestamp=datetime.now(),
        )
    db.session.add(transaction)


@event.listens_for(Component, "before_delete")
def before_component_delete(mapper, connection, target):
    transaction = DatabaseTransaction(
        objectId=target.id,
        tableName="component",
        operation="delete",
        changes=f"Component ID {target.id} was deleted",
        timestamp=datetime.utcnow(),
    )
    db.session.add(transaction)
