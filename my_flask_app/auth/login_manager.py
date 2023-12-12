""" Filename: login_manager.py - Directory: auth 
"""
from flask_login import LoginManager

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    from database.models import User

    return User.query.get(int(user_id))
