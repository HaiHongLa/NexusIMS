"""
Database models for inventory management.

This module defines database models for product inventory and component inventory. 
These models represent the inventory of products and components stored at various 
production facilities.
"""

from extensions import db
from datetime import datetime
from models.dbUtils import BaseModel


class ProductInventory(db.Model, BaseModel):
    """
    Represents the inventory of products within the database.

    Attributes:
        id (int): The unique identifier for the inventory record.
        productId (int): Foreign key referencing the product stored in this inventory.
        count (int): The quantity of the product available at the specified location.
        productionFacilityId (int): Foreign key referencing the production facility where the product is stored.
        lastUpdated (datetime): The timestamp when the inventory record was last updated.
        lastUpdatedByUserId (int): The ID of the user who last updated the inventory record.

    Methods:
        __repr__: Returns a string representation of the product inventory.
    """

    __tablename__ = "productInventory"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    productId = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="CASCADE"))
    count = db.Column(db.Integer, nullable=False)
    productionFacilityId = db.Column(
        db.Integer,
        db.ForeignKey("productionFacilities.id", ondelete="CASCADE"),
    )
    lastUpdated = db.Column(db.DateTime, nullable=True, default=datetime.now())
    lastUpdatedByUserId = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"{self.count} product {self.productId} at facility {self.facilityId}"


class ComponentInventory(db.Model, BaseModel):
    """
    Represents the inventory of components within the database.

    Attributes:
        id (int): The unique identifier for the inventory record.
        componentId (int): Foreign key referencing the component stored in this inventory.
        count (int): The quantity of the component available at the specified location.
        productionFacilityId (int): Foreign key referencing the production facility where the component is stored.
        lastUpdated (datetime): The timestamp when the inventory record was last updated.
        lastUpdatedByUserId (int): The ID of the user who last updated the inventory record (nullable).

    Methods:
        __repr__: Returns a string representation of the component inventory.
    """

    __tablename__ = "componentInventory"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    componentId = db.Column(
        db.Integer, db.ForeignKey("components.id", ondelete="CASCADE")
    )
    count = db.Column(db.Integer, nullable=False)
    productionFacilityId = db.Column(
        db.Integer,
        db.ForeignKey("productionFacilities.id", ondelete="CASCADE"),
    )
    lastUpdated = db.Column(db.DateTime, nullable=False, default=datetime.now())
    lastUpdatedByUserId = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"{self.count} component {self.productId} at facility {self.facilityId}"
