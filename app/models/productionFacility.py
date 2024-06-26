"""
Database model for production facilities.

This module defines the database model for production facilities. It includes fields 
for various attributes of production facilities and event listeners for recording 
database transactions after insert and update operations.
"""

from sqlalchemy import event
from extensions import db
from models.dbUtils import BaseModel
from models.transaction import DatabaseTransaction
from datetime import datetime


class ProductionFacility(db.Model, BaseModel):
    __tablename__ = "productionFacilities"

    """
    Represents a production facility in the database.

    Attributes:
        id (int): The unique identifier for the facility.
        name (str): The name of the facility.
        contactInfo (str): Contact information for the facility.
        longitude (float): Longitude coordinate of the facility.
        latitude (float): Latitude coordinate of the facility.
        isOperating (bool): Indicates whether the facility is operating.
        streetAddress (str): The street address of the facility.
        city (str): The city where the facility is located.
        stateProvinceRegion (str): The state, province, or region where the facility is located.
        postalCode (str): The postal code for the facility.
        country (str): The country where the facility is located.
        notes (str): Additional notes about the facility.

    Methods:
        __repr__: Returns a string representation of the facility.
    """

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256), nullable=False)
    contactInfo = db.Column(db.String(256), nullable=True)
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    isOperating = db.Column(db.Boolean, nullable=False, default=True)
    streetAddress = db.Column(db.String(256), nullable=True)
    city = db.Column(db.String(256), nullable=True)
    stateProvinceRegion = db.Column(db.String(256), nullable=True)
    postalCode = db.Column(db.String(64), nullable=True)
    country = db.Column(db.String(128), nullable=True)
    notes = db.Column(db.Text)

    def __repr__(self):
        """
        Returns a string representation of the facility.

        Returns:
            str: A string representation of the facility, including its name and ID.
        """
        return f"<Facility {self.id}: {self.name}>"
        return f"<Facility {self.id}: {self.name}>"


@event.listens_for(ProductionFacility, "after_insert")
def after_productionFacility_insert(mapper, connection, target):
    transaction = DatabaseTransaction(
        objectId=target.id,
        tableName="productionFacility",
        operation="insert",
        changes=f"New facility created with Name: {target.name},"
        + f" Country: {target.country}, ContactInfo: {target.contactInfo}",
        timestamp=datetime.now(),
    )
    db.session.add(transaction)


@event.listens_for(ProductionFacility, "after_update")
def after_productionFacility_update(mapper, connection, target):
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
            tableName="productionFacility",
            operation="update",
            changes=f"Facility {change_description}",
            timestamp=datetime.now(),
        )
    db.session.add(transaction)


@event.listens_for(ProductionFacility, "before_delete")
def before_productionFacility_delete(mapper, connection, target):
    """
    Event listener function triggered after a production facility is updated.

    Args:
        mapper: The mapper object managing state.
        connection: The database connection for the update operation.
        target: The updated production facility object.
    """

    transaction = DatabaseTransaction(
        objectId=target.id,
        tableName="productionFacility",
        operation="delete",
        changes=f"Facility ID {target.id} was deleted",
        timestamp=datetime.utcnow(),
    )
    db.session.add(transaction)
