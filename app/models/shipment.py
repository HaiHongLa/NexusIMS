"""
This section store the orders' shipment information. Users can create the shipment orders
"""

from sqlalchemy import event
from extensions import db
from models.dbUtils import BaseModel
from models.transaction import DatabaseTransaction
from datetime import datetime


class shipment(db.Model, BaseModel):
    """
    Required data are the name and id of the shiper and the location of it
    """

    __tablename__ = "shipment"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256), nullable=True)  # TODO: nullable should be False
    contactInfo = db.Column(db.String(256), nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    latitude = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f"<shipment {self.id}: {self.name}>"
