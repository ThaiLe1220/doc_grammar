""" Filename: db_setup.py - Directory: my_flask_app/database 
"""
from flask_sqlalchemy import SQLAlchemy
from .models import db


def setup_database(app):
    with app.app_context():
        db.init_app(app)
        db.create_all()
