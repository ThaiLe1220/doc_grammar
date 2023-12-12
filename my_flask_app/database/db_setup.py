""" Filename: db_setup.py - Directory: my_flask_app/database 

This module provides a utility function for initializing and setting up
the database for the Flask application. 

"""
from .models import db


def setup_database(app):
    """
    Initializes and sets up the database for the Flask application.

    This function binds the database instance with the provided Flask application
    context and creates all necessary database tables according to the defined
    models.

    Args:
        app (Flask): The Flask application instance to which the database
        will be bound and initialized.
    """
    with app.app_context():
        db.init_app(app)
        db.create_all()
