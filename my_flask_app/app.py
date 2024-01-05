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
    jsonify,
    request,
    session,
)
from flask_login import current_user, login_user, logout_user, login_required
from database.db_setup import setup_database
from database.models import db, User, FileUpload
from file_handling.file_routes import file_blueprint
from auth.oauth import oauth, configure_oauth
from auth.login_manager import login_manager
import stripe


app = Flask(__name__)

# setting up stripe api keys
app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51OReIZCS2kdynUVumJcWQAWQ1xsXuApU3cNWwVBc88D1rSFN7uI5EQErxTk54XsP8mypOQFSfkQR4oj6DwivLdpo00pRdYPqjE'
app.config['STRIPE_SECRET_KEY'] = 'sk_test_51OReIZCS2kdynUVuNPDL0wvlDqyz25JSnO3z3qql6Ivz9cMnn3eBQQ0s7LMjsXwi1fYggjVEiBGGjItuWgwDLWdP00TdfoLxmo'
app.config['STRIPE_ENDPOINT_SECRET'] = 'your_stripe_webhook_secret'

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://huyhua:namhuy1211@localhost/doc_grammar" 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Suppress a warning
app.config["SECRET_KEY"] = "eugene_secret"  # Flash messages

if not os.path.exists("file_uploads"):
    os.makedirs("file_uploads")

app.config["UPLOAD_FOLDER"] = "file_uploads"
stripe.api_key = app.config['STRIPE_SECRET_KEY']

setup_database(app)
configure_oauth(app)
login_manager.init_app(app)

# Register blueprints
app.register_blueprint(file_blueprint, url_prefix="/files")


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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure all tables are created
    app.run(debug=True)

@app.route("/subscribe", methods=["GET", "POST"])
@login_required
def subscribe():
    if request.method == "POST":
        try:
            # Create a checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': 'price_1OSNSqCS2kdynUVuQuxffvTD',  # replace with your actual price ID
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=url_for('index', _external=True),
                cancel_url=url_for('index', _external=True),
            )

            return jsonify({'id': checkout_session.id})
        except stripe.error.StripeError as e:
            return jsonify({'error': str(e)}), 403

    return render_template("index.html",
        checkout_session_id = session['id'],
        checkout_public_key = app.config['STRIPE_PUBLIC_KEY'])


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, app.config['STRIPE_ENDPOINT_SECRET']
        )
    except ValueError as e:
        print('Invalid payload')
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        print('Invalid signature')
        return 'Invalid signature', 400

    # Handle the event
    handle_stripe_event(event)

    return '', 200

def handle_stripe_event(event):
    # Handle different types of Stripe events (payment success, subscription update, etc.)
    if event['type'] == 'checkout.session.completed':
        # Handle successful subscription
        handle_successful_subscription(event)
    elif event['type'] == 'invoice.payment_failed':
        # Handle failed payment
        handle_failed_payment(event)
    # Add more cases for other events as needed

def handle_successful_subscription(event):
    # Logic to handle a successful subscription
    customer_id = event['data']['object']['customer']
    user = User.query.filter_by(stripe_customer_id=customer_id).first()
    if user:
        user.account_type = 'pro'  # Upgrade user account to pro
        db.session.commit()

def handle_failed_payment(event):
    # Logic to handle a failed payment
    # You might want to notify the user or take other actions
    pass

# @app.route("/check_db")
# def check_database_connection():
#     try:
#         db.session.query(FileUpload).first()
#         return "Database connection successful. Happy coding"
#     except Exception as e:
#         return f"Database connection error: {str(e)}"
