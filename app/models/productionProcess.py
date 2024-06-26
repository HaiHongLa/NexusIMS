"""
Database model for production processes.

This module defines the database model for production processes. Each 
process take a certain amount of time and transforms an amount of components 
into a product.
"""

from sqlalchemy import event
from extensions import db
from models.dbUtils import BaseModel
from models.transaction import DatabaseTransaction
from datetime import datetime


class ProductionProcess(db.Model, BaseModel):
    __tablename__ = "productionProcesses"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    requires = db.Column(
        db.Integer,
        db.ForeignKey("ComponentRequirement.id", ondelete="CASCADE"),
    )
    product = db.Column(
        db.Integer,
        db.ForeignKey("products.id", ondelete="CASCADE"),
    )
    minutes = db.Column(db.Integer, nullable=False)
    lastUpdated = db.Column(db.DateTime, nullable=False, default=datetime.now())
    lastUpdatedByUserId = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"{self.minutes} time {self.id} produces {self.product}"


class ComponentsRequired(db.Model, BaseModel):
    __tablename__ = "ComponentsRequired"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    componentId = db.Column(
        db.Integer, db.ForeignKey("components.id", ondelete="CASCADE")
    )
    count = db.Column(db.Integer, nullable=False)
    processId = db.Column(
        db.Integer,
        db.ForeignKey("productionProcesses.id", ondelete="CASCADE"),
    )

    def __repr__(self):
        return (
            f"{self.count} {self.componentId} components for process {self.processId}"
        )
