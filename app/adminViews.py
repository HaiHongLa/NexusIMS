"""
Custom views for Flask-Admin interface.

This module contains custom view classes for Flask-Admin, which provide additional functionality and access control for managing various data models within the application.
"""

from flask import render_template, url_for, session, redirect
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from markupsafe import Markup


class BaseView:
    """Base view class providing access control methods for Flask-Admin views."""

    def is_accessible(self):
        """Check if the current user session contains a username."""
        return "username" in session

    def inaccessible_callback(self, name, **kwargs):
        """Redirect users without a valid session to the login page."""
        return redirect(url_for("login"))


class CustomAdminIndexView(BaseView, AdminIndexView):
    """Custom index view for Flask-Admin."""

    @expose("/")
    def index(self):
        context = dict()
        context["msg"] = "Welcome to Nexus Admin!"
        return self.render("admin/index.html", context=context)


class CustomView(BaseView, ModelView):
    """Custom model view for Flask-Admin with added access control."""

    can_view_details = True


class UserView(BaseView, ModelView):
    """View for managing user data."""

    column_exclude_list = ["passwordHash", "role"]
    column_labels = {
        "username": "Username",
        "firstName": "First Name",
        "lastName": "Last Name",
        "phoneNumber": "Phone Number",
        "email": "Email",
    }


class ProductionFacilityView(BaseView, ModelView):
    """View for managing production facility data."""

    can_view_details = True
    column_list = [
        "name",
        "contactInfo",
        "longitude",
        "latitude",
        "isOperating",
        "streetAddress",
        "city",
        "stateProvinceRegion",
        "country",
    ]
    column_searchable_list = [
        "name",
        "contactInfo",
        "city",
        "stateProvinceRegion",
        "country",
    ]
    column_filters = ["name", "city", "stateProvinceRegion", "country", "isOperating"]
    column_sortable_list = [
        "name",
        "isOperating",
        "longitude",
        "latitude",
        "city",
        "stateProvinceRegion",
        "country",
    ]
    column_labels = {
        "contactInfo": "Contact Information",
        "streetAddress": "Street Address",
        "stateProvinceRegion": "State/Province/Region",
        "postalCode": "Postal Code",
        "isOperating": "Is Operating",
    }
    column_formatters = {
        "name": lambda v, c, m, p: Markup(
            f'<a href="{url_for("facilityInventory", facilityId=m.id)}">{m.name}</a>'
        )
    }
    column_editable_list = [
        "isOperating",
    ]

    # Override the default query to order by isOperating
    def get_query(self):
        return self.session.query(self.model).order_by(self.model.isOperating.desc())


class ProductView(BaseView, ModelView):
    """View for managing product data."""

    can_view_details = True
    column_exclude_list = ["description", "specs"]
    column_searchable_list = ["id", "category", "brand", "model"]
    column_filters = ["category", "brand", "available"]


class ProductInventoryView(BaseView, ModelView):
    """View for viewing product inventory data."""

    column_hide_backrefs = False
    can_view_details = False
    can_edit = False
    can_create = False
    column_list = [
        "productId",
        "count",
        "productionFacilityId",
        "lastUpdated",
        "lastUpdatedByUserId",
    ]
    column_filters = ["productId", "productionFacilityId"]


class DatabaseTransactionView(ModelView):
    """View for viewing database transaction logs."""

    can_create = False
    can_delete = False
    can_edit = False
    column_filters = ["objectId", "tableName", "operation", "timestamp"]
    column_searchable_list = ["objectId", "operation", "tableName"]
    column_list = ["objectId", "tableName", "operation", "changes", "timestamp"]
    column_default_sort = ("timestamp", True)
    column_labels = {
        "objectId": "Object ID",
        "tableName": "Table Type",
        "operation": "Operation",
        "changes": "Changes",
        "timestamp": "Timestamp",
    }


class ShipmentView(BaseView, ModelView):
    can_view_details = True
