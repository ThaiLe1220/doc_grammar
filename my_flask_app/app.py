""" Filename: app.py - Directory: my_flask_app 

This file is the main entry point for a Flask web application that handles file uploads, 
grammar checking, and user authentication via Google OAuth.

The application is configured with database settings, file upload paths, and OAuth settings. 
It includes routes for user authentication, file upload, download, deletion and grammar corrections.

Key Components:
- Flask app initialization with configuration settings.
- Database setup and OAuth configuration.
- Registration of the file handling blueprint for managing file-related routes.
- Routes for login, logout, and user authentication callback.
- The main index route to display the uploaded files and their grammar corrections.
- Running the Flask app in debug mode within a protected main block.

"""
import os
import secrets
from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    session,
)
from flask_login import current_user, login_user, logout_user, login_required
from database.db_setup import setup_database
from database.models import db, User, FileUpload
from file_handling.file_routes import file_blueprint
from auth.oauth import oauth, configure_oauth
from auth.login_manager import login_manager

app = Flask(__name__)

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://eugene:eugene@localhost/doc_grammar"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Suppress a warning
app.config["SECRET_KEY"] = "eugene_secret"  # Flash messages

if not os.path.exists("file_uploads"):
    os.makedirs("file_uploads")

app.config["UPLOAD_FOLDER"] = "file_uploads"

setup_database(app)
configure_oauth(app)
login_manager.init_app(app)

# Register blueprints
app.register_blueprint(file_blueprint, url_prefix="/files")


# @app.route("/check_db")
# def check_database_connection():
#     try:
#         db.session.query(FileUpload).first()
#         return "Database connection successful. Happy coding"
#     except Exception as e:
#         return f"Database connection error: {str(e)}"


@app.route("/login")
def login():
    """
    Initiates the OAuth login process with Google.

    Generates a nonce token for security, saves it in the session, and redirects
    the user to Google's OAuth authorization URL.

    Returns:
        Response: A redirect response to Google's OAuth authorization URL.
    """
    # Generate a nonce and save it in the session for later validation
    nonce = secrets.token_urlsafe()
    session["nonce"] = nonce
    redirect_uri = url_for("authorize", _external=True)
    return oauth.google.authorize_redirect(redirect_uri, nonce=nonce)


@app.route("/login/callback")
def authorize():
    """
    Handles the OAuth callback from Google.

    Extracts the token from the callback, retrieves the nonce from the session,
    validates the token, and logs in the user if authentication is successful.

    Returns:
        Response: A redirect to the homepage after successful login or an error message.
    """
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
        user = User(google_id=user_info["sub"], email=user_info["email"])
        db.session.add(user)
        db.session.commit()
    login_user(user)
    return redirect("/")


@login_manager.user_loader
def load_user(user_id):
    """
    Loads a user given their ID.

    Args:
        user_id (int): Unique identifier of the user.

    Returns:
        User: The user object corresponding to the given ID.
    """
    return User.query.get(int(user_id))


@app.route("/logout")
@login_required
def logout():
    """
    Logs out the current user.

    Ends the user session and redirects to the homepage.

    Returns:
        Response: A redirect response to the homepage.
    """
    logout_user()
    return redirect("/")


@app.route("/")
def index():
    """
    Displays the homepage of the application.

    Fetches uploaded files and their grammar corrections, if available,
    from the database and renders them on the homepage.

    Returns:
        str: Rendered HTML content for the homepage.
    """
    files = FileUpload.query.all()
    file_id = session.get("file_id")
    corrections = None

    if file_id:
        file = FileUpload.query.get(file_id)
        if file:
            corrections = file.corrections

    return render_template(
        "index.html", files=files, corrections=corrections, current_user=current_user
    )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure all tables are created
    app.run(debug=True)
