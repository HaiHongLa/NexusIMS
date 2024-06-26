"""
Flask web application for managing inventory and user authentication.

This application provides functionality for managing inventory, user authentication, 
and dashboard display.

Routes:
- '/' : Home page.
- '/login' : User login page.
- '/inventory' : Inventory overview page.
- '/inventory/<int:facilityId>' : Detailed inventory view for a specific facility.
- '/save-changes' : Endpoint for saving inventory changes.
- '/infoModal' : Endpoint for displaying an information modal.
- '/logout' : Endpoint for user logout.
- '/signup' : User signup page.
- '/information' : Information page.
- '/dashboard' : Dashboard page.

"""

from flask import (
    Flask,
    redirect,
    render_template,
    request,
    session,
    abort,
    jsonify,
    url_for,
)
from config import Config
from extensions import db
from flask_admin import Admin
from flask_oauthlib.client import OAuth
from adminViews import (
    CustomAdminIndexView,
    CustomView,
    ProductionFacilityView,
    ProductView,
    UserView,
    DatabaseTransactionView,
    ShipmentView,
)
from models.component import Component
from models.inventory import ProductInventory, ComponentInventory
from models.product import Product
from models.productionFacility import ProductionFacility
from models.user import User
from models.transaction import DatabaseTransaction
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
oauth = OAuth(app)

admin = Admin(
    app,
    name="Nexus Admin",
    template_mode="bootstrap4",
    index_view=CustomAdminIndexView(name="Home"),
)
admin.add_view(UserView(User, db.session, name="Personnel"))
admin.add_view(ProductView(Product, db.session, name="Products"))
admin.add_view(CustomView(Component, db.session, name="Components"))
admin.add_view(
    ProductionFacilityView(ProductionFacility, db.session, name="Facilities")
)


admin.add_view(
    DatabaseTransactionView(
        DatabaseTransaction, db.session, name="Database Transactions"
    )
)

google = oauth.remote_app(
    "google",
    consumer_key=os.getenv("GOOGLE_CONSUMER_KEY"),
    consumer_secret=os.getenv("GOOGLE_CONSUMER_SECRET"),
    request_token_params={
        "scope": "email",
    },
    base_url="https://www.googleapis.com/oauth2/v1/",
    request_token_url=None,
    access_token_method="POST",
    access_token_url="https://accounts.google.com/o/oauth2/token",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
)


@app.route("/")
def home():
    """Render the home page."""
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Render the login page and handle user authentication."""

    # checks for POST vs GET request
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        # Checks if password attached to username is in system and redirects based on results
        if user and user.checkPassword(password):
            session["username"] = username
            return redirect("/dashboard")
        # returns to login if password and/or username is not in system
        else:
            return redirect("/login")
    return render_template("/login.html")


# Define the route for initiating Google OAuth login
@app.route("/googleLogin")
def googleLogin():
    return google.authorize(callback=url_for("googleAuthorized", _external=True))


# Define the route for handling the Google OAuth callback
@app.route("/googleLogin/callback")
def googleAuthorized():
    resp = google.authorized_response()

    if resp is None or resp.get("access_token") is None:
        return "Access denied: reason={} error={}".format(
            request.args["error_reason"], request.args["error_description"]
        )

    session["googleToken"] = (resp["access_token"], "")
    userInfo = google.get("userinfo")
    email = userInfo.data.get("email")
    # Here i will check if details provided are correct
    user = User.query.filter_by(email=email).first()
    if user:
        # If the user exists, add the user's email to the session
        session["username"] = user.username
        session["email"] = str(email)
        return redirect("/dashboard")
    else:
        # If the user does not exist, redirect to the login page
        return redirect("/login")


# Define the function to retrieve the Google OAuth token
@google.tokengetter
def getGoogleOAuthToken():
    return session.get("googleToken")


@app.route("/inventory")
def inventoryHome():
    """Render the inventory overview page."""
    facilities = [facility.toDict() for facility in ProductionFacility.query.all()]
    return render_template("inventory.html", facilities=facilities)


@app.route("/inventory/<int:facilityId>")
def facilityInventory(facilityId):
    """Render the detailed inventory view for a specific facility."""
    facility = db.session.get(ProductionFacility, facilityId)
    if facility:
        productEntries = [
            entry.toDict()
            for entry in db.session.query(ProductInventory).filter(
                ProductInventory.productionFacilityId == facility.id
            )
        ]

        for entry in productEntries:
            entry["product"] = (
                db.session.query(Product).get(entry["productId"]).toDict()
            )

        componentEntries = [
            entry.toDict()
            for entry in db.session.query(ComponentInventory).filter(
                ComponentInventory.productionFacilityId == facility.id
            )
        ]

        for entry in componentEntries:
            entry["component"] = (
                db.session.query(Component).get(entry["componentId"]).toDict()
            )

        return render_template(
            "facilityInventory.html",
            facility=facility,
            productEntries=productEntries,
            componentEntries=componentEntries,
        )
    else:
        abort(404)


@app.route("/save-changes", methods=["POST"])
def saveInventoryChanges():
    """Endpoint for saving inventory changes."""
    data = dict(request.json)
    errors = list()
    entryTypeMap = {"product": ProductInventory, "component": ComponentInventory}
    for newEntry in data["changesList"]:
        try:
            if newEntry["type"] not in entryTypeMap:
                raise Exception("Invalid inventory entry type.")
            entry = (
                entryTypeMap[newEntry["type"]]
                .query.filter_by(id=newEntry["entryId"])
                .first()
            )
            entry.count = newEntry["quantity"]
            db.session.add(entry)
            db.session.commit()
        except Exception as e:
            errors.append(str(e))

    if errors:
        resp = {
            "msg": f"Errors occured on {len(errors)}/{len(data['changesList'])} updates.",
            "errors": errors,
        }
    else:
        resp = {"msg": "Inventory updated successfully."}
    return jsonify(resp)


@app.route("/add-entry")
def addEntry():
    """Render the form for adding an inventory entry."""
    return render_template("addEntry.html")


@app.route("/infoModal", methods=["GET", "POST"])
def infoModal():
    """Render the information modal."""
    return render_template("admin/InfoModal.html")


@app.route("/logout")
def logout():
    """Handle user logout."""
    # removes user from session and redirects to intro page
    session.pop("username", None)
    return redirect("/")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Get form data
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if username or email already exists in the database
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing_user:
            return redirect("/login")

        # Create a new user
        new_user = User(username=username, email=email)
        new_user.setPassword(
            password
        )  # Set the password using the method from the User model

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Redirect to the login page
        return redirect("/login")

    return render_template("signup.html")


@app.route("/information")
def info():
    """Render the information page."""
    return render_template("information.html")


@app.route("/dashboard")
def dashboard():
    """Render the dashboard page."""
    return render_template("dashboard.html")


@app.route("/map-data")
def facilityMapData():
    facilities = ProductionFacility.query.all()
    data = {
        "lat": [f.latitude for f in facilities],
        "lon": [f.longitude for f in facilities],
        "text": [f.name for f in facilities],
    }
    return jsonify(data)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=5001, debug=True, host="0.0.0.0")
