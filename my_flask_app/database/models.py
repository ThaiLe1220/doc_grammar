""" Filename: models.py - Directory: my_flask_app/database 

This module defines the database models used in the Flask application.
It includes the User model representing authenticated users and the FileUpload
model representing uploaded files along with their attributes.

"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """
    User model representing authenticated users in the system.

    Args:
        id (int): Unique identifier of the user.
        google_id (str): Unique Google identifier for OAuth.
        email (str): Email address of the user.
        name (str): Full name of the user.
        given_name (str): Given name of the user.
        family_name (str): Family name of the user.
        picture (str): URL of the user's profile picture.
        locale (str): The user's preferred locale/language.
    """
    
    id = db.Column(db.Integer, primary_key=True) # customer id
    google_id = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120), unique=True)
    name = db.Column(db.String(255))
    given_name = db.Column(db.String(255))
    family_name = db.Column(db.String(255))
    picture = db.Column(db.String(255))
    locale = db.Column(db.String(10))
    account_type = db.Column(db.String(20), default="Free")
    stripe_customer_id = db.Column(db.String(50), unique=True)
    subscription_purchased = db.Column(db.Boolean, default=False)
    daily_upload_count = db.Column(db.Integer, default=0)
    last_upload_date = db.Column(db.DateTime, server_default=db.func.now())
    expired_date = db.Column(db.DateTime, server_default=db.func.now())

class FileUpload(db.Model):
    """
    FileUpload model representing files uploaded by users.

    Args:
        id (int): Unique identifier of the file upload.
        file_name (str): Name of the uploaded file.
        file_path (str): Server path of the uploaded file.
        upload_time (datetime): Time of the upload.
        corrections (JSONB): Stored corrections for the file.
    """

    __tablename__ = "file_uploads"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Assuming 'user' is your user table
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.Text, nullable=False)
    file_size = db.Column(db.Double, default=0)
    upload_time = db.Column(db.DateTime, server_default=db.func.now())
    corrections = db.Column(JSONB)