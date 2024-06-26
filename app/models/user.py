"""
Database model for users.

This module defines the database model for users. It includes fields for user information such as username, password hash, role, first name, last name, phone number, email, and title. It also provides methods for setting and checking passwords, as well as converting user objects to dictionaries.
"""

from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import event
from extensions import db
from models.dbUtils import BaseModel
from models.transaction import DatabaseTransaction
from datetime import datetime


class User(db.Model, BaseModel):
    """
    Represents a user in the database.

    Attributes:
        id (int): The unique identifier for the user.
        username (str): The username of the user, which must be unique.
        passwordHash (str): The hashed password of the user.
        role (int): The role identifier for the user (nullable, default: None).
        firstName (str): The first name of the user.
        lastName (str): The last name of the user.
        phoneNumber (str): The phone number of the user.
        email (str): The email address of the user.
        title (str): The title or position of the user.

    Methods:
        __repr__: Returns a string representation of the user.
        toDict: Converts the user object into a dictionary, excluding sensitive data like the password hash.
        setPassword: Sets the user's password by generating a hashed version.
        checkPassword: Verifies the user's password by checking against the stored hash.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    passwordHash = db.Column(db.String(512), nullable=False)
    role = db.Column(
        db.Integer, nullable=True
    )  # need to change to nullable = False later
    firstName = db.Column(db.String(64), nullable=True)
    lastName = db.Column(db.String(64), nullable=True)
    phoneNumber = db.Column(db.String(64), nullable=True)
    email = db.Column(db.String(80), unique=False, nullable=True)
    title = db.Column(db.String(128), nullable=True)

    def __repr__(self):
        return "<User %r>" % self.username

    def toDict(self):
        """
        Converts the user object into a dictionary.

        Returns:
            dict: A dictionary representation of the user object, excluding the password hash.
        """
        userDict = super().toDict()
        dictionary = {key: val for key, val in userDict if key != "passwordHash"}
        return dictionary

    def setPassword(self, password):
        """
        Sets the user's password by generating a hashed version.

        Args:
            password (str): The raw password to be hashed and stored.
        """
        self.passwordHash = generate_password_hash(password)

    def checkPassword(self, password):
        """
        Verifies the user's password by checking it against the stored hash.

        Args:
            password (str): The raw password to be checked.

        Returns:
            bool: True if the password is correct, False otherwise.
        """
        return check_password_hash(self.passwordHash, password)


@event.listens_for(User, "after_update")
def after_user_update(mapper, connection, target):
    """
    Event listener triggered after a user is updated in the database.

    Args:
        mapper: The mapper object managing state.
        connection: The database connection used for the update operation.
        target: The updated user object.
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
            tableName="user",
            operation="update",
            changes=change_description,
            timestamp=datetime.now(),
        )
    db.session.add(transaction)
    print(f"User ID: {target.id} updated.")


@event.listens_for(User, "before_delete")
def before_user_delete(mapper, connection, target):
    """
    Event listener triggered before a user is deleted from the database.

    Args:
        mapper: The mapper object managing state.
        connection: The database connection used for the delete operation.
        target: The user object to be deleted.
    """
    # Create a DatabaseTransaction record for logging the deletion
    transaction = DatabaseTransaction(
        objectId=target.id,
        tableName="user",
        operation="delete",
        changes=f"User ID {target.id} was deleted",
        timestamp=datetime.now(),
    )
    # Add the transaction to the session
    db.session.add(transaction)
