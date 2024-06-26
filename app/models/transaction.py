"""
Database model for database transactions.

This module defines the database model for recording database transactions. It includes 
fields for storing information about the operation performed, the affected table, the 
changes made, and the timestamp of the transaction.
"""

from extensions import db
from models.dbUtils import BaseModel
from datetime import datetime


class DatabaseTransaction(db.Model, BaseModel):
    __tablename__ = "databaseTransactions"

    id = db.Column(db.Integer, primary_key=True)  # The ID for the transactions
    objectId = db.Column(
        db.Integer, nullable=False
    )  # The ID of products, components, facilities
    tableName = db.Column(db.String(50), nullable=False)
    operation = db.Column(db.String(50), nullable=False)
    changes = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return (
            f"<Transaction {self.operation} for {self.tableName.capitalize()}"
            + " ID {self.objectId} at {self.timestamp}>"
        )
