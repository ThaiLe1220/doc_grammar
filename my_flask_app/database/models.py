""" Filename: models.py - Directory: my_flask_app/database 
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120), unique=True)


class FileUpload(db.Model):
    __tablename__ = "file_uploads"
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False, unique=True)
    file_path = db.Column(db.Text, nullable=False)
    upload_time = db.Column(db.DateTime, server_default=db.func.now())
    corrections = db.Column(JSONB)
