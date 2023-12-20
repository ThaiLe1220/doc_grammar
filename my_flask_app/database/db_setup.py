""" Filename: db_setup.py - Directory: my_flask_app/database 

"""
from flask_migrate import Migrate
from my_flask_app.database.models import db


def setup_database(app):
    with app.app_context():
        db.init_app(app)
        Migrate(app, db)
