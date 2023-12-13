""" Filename: db_setup.py - Directory: my_flask_app/database 

This module provides a utility function for initializing and setting up
the database for the Flask application. 

"""
from flask_migrate import Migrate
from .models import db


def setup_database(app):
    """
    Configures and prepares the database for use with the Flask application.
    This function initializes the SQLAlchemy database object and sets up Flask-Migrate
    for handling database migrations. It ensures that the database and the Flask app
    are properly connected and ready to handle model operations.

    Args:
        app (Flask): The Flask application instance with which the database is to be integrated.
    Note:
        Make sure to run `flask db init` to initialize migrations if you haven't already,
        followed by `flask db migrate` and `flask db upgrade` to apply migrations.
    """
    with app.app_context():
        db.init_app(app)
        Migrate(app, db)
