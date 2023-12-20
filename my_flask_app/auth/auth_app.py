""" Filename: auth_app.py - Directory: my_flask_app/auth  
"""
import secrets
import os
from flask import Flask, redirect, url_for, session, render_template
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from my_flask_app.database.db_setup import setup_database
from my_flask_app.database.models import db, User
from .oauth import oauth, configure_oauth

app = Flask(__name__, template_folder="/app/templates")

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

setup_database(app)

configure_oauth(app)
login_manager = LoginManager()
login_manager.init_app(app)


# User Loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Login Route
@app.route("/login")
def login():
    nonce = secrets.token_urlsafe()
    session["nonce"] = nonce
    redirect_uri = url_for("authorize", _external=True)
    return oauth.google.authorize_redirect(redirect_uri, nonce=nonce)


# OAuth Callback
@app.route("/login/callback")
def authorize():
    token = oauth.google.authorize_access_token()
    nonce = session.pop("nonce", None)  # Retrieve and remove the nonce from the session
    user_info = oauth.google.parse_id_token(token, nonce=nonce)

    # Verify the issuer.
    issuer = user_info.get("iss")
    if issuer not in ["https://accounts.google.com", "accounts.google.com"]:
        # Handle the invalid issuer.
        return "Invalid issuer.", 400

    user = User.query.filter_by(google_id=user_info["sub"]).first()
    if user is None:
        user = User(
            google_id=user_info["sub"],
            email=user_info["email"],
            name=user_info.get("name"),
            given_name=user_info.get("given_name"),
            family_name=user_info.get("family_name"),
            picture=user_info.get("picture"),
            locale=user_info.get("locale"),
        )
        db.session.add(user)
    else:
        # Update the existing user with any new information
        user.name = user_info.get("name")
        user.given_name = user_info.get("given_name")
        user.family_name = user_info.get("family_name")
        user.picture = user_info.get("picture")
        user.locale = user_info.get("locale")

    db.session.commit()
    login_user(user)
    return redirect(url_for("index"))


# Logout Route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


# Index Route (optional, for testing)
@app.route("/")
def index():
    return render_template("index.html", current_user=current_user)


if __name__ == "__main__":
    app.run(debug=True)
