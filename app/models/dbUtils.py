"""
Base model utilities for database operations.

This module provides utility functions for database operations such as converting model instances to dictionaries, saving instances to the database, and deleting instances from the database.
"""

from extensions import db


class BaseModel:
    def toDict(self):
        dictionary = {
            key: val for key, val in vars(self).items() if not key.startswith("_")
        }
        return dictionary

    def saveToDb(self):
        db.session.add(self)
        db.session.commit()

    def deleteFromDb(self):
        db.session.delete(self)
        db.session.commit()
