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
    """

    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120), unique=True)


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
    file_name = db.Column(db.String(255), nullable=False, unique=True)
    file_path = db.Column(db.Text, nullable=False)
    upload_time = db.Column(db.DateTime, server_default=db.func.now())
    corrections = db.Column(JSONB)
