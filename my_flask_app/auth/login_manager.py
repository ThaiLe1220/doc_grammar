""" Filename: login_manager.py - Directory: auth 

This module defines and configures the Flask-Login manager for the Flask application.
It includes the user loader callback function that is used by Flask-Login to load
user objects from user IDs, enabling user session management.

"""
from flask_login import LoginManager

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    """
    Callback function for loading a user from the user ID.

    This function is used by Flask-Login to manage user sessions. It loads
    a user object from the given user ID, which is then used to represent the
    authenticated user.

    Args:
        user_id (int): The ID of the user to load.

    Returns:
        User: An instance of the User model corresponding to the user_id, or
              None if no such user exists.
    """
    from database.models import User

    return User.query.get(int(user_id))
