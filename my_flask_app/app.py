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
    abort,
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
app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51OVEkqDAl3fqs0z5WYJHtSc1Jn2WZD4w7vV7rVOULeHvdgYSoXxa415eCxTnYBZ0xTXCqDBdW5xla4hw1xyjumQQ00T45kDMNP'
app.config['STRIPE_SECRET_KEY'] = 'sk_test_51OVEkqDAl3fqs0z5tlfYXaUWj8cLjU8eMHhEp4xgxjdt5IbVxv4Mh7qJzkiul1XRVflXNX79Q4zNfjnVacLeje8s00usdgCVQf'
endpoint_secret = 'whsec_8468e026695e3bd1d7d474cccf9b99bd6f11adb10d8692940eddc6c2e37dbc3f'
Domain = 'http://localhost:5000'

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://huynguyen284:password@localhost/doc_grammar" 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Suppress a warning
app.config["SECRET_KEY"] = "eugene_secret"  # Flash messages

if not os.path.exists("file_uploads"):
    os.makedirs("file_uploads")

app.config["UPLOAD_FOLDER"] = "file_uploads"
stripe.api_key = app.config['STRIPE_SECRET_KEY']

from flask_migrate import Migrate

# Assuming `app` and `db` are your Flask and SQLAlchemy instances
migrate = Migrate(app, db)

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

@app.route("/subscribe", methods=["GET", "POST"])
@login_required
def subscribe():
    print("Entered the /subscribe route")  # Debugging print statement
 
    if request.method == "POST":
        print("Handling a POST request")  # Debugging print statement
 
        try:
            # Create a checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": "price_1OVFVUDAl3fqs0z5BJEqJHCV",
                        "quantity": 1,
                    }
                ],
                mode="subscription",
                success_url=url_for("handle_subscription_success", _external=True)
                + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=url_for("index", _external=True),
            )
 
            print(
                f"Checkout session created: {checkout_session.id}"
            )  # Debugging print statement
 
            # Redirect to the checkout session
            return jsonify({"id": checkout_session.id})
        except stripe.error.StripeError as e:
            app.logger.error(f"Stripe error: {str(e)}")
            print(f"Stripe error: {str(e)}")  # Debugging print statement
            return jsonify(error=str(e)), 403
 
    print("Handling a GET request")  # Debugging print statement
 
    # If it's a GET request, return the main page with the Stripe public key
    return render_template(
        "index.html", stripe_public_key=app.config["STRIPE_PUBLIC_KEY"]
    )

@app.route('/webhook', methods=['POST'])
def webhook():
    print('webhook called')
    event = None
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        print('Invalid payload')
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print('Invalid signature')
        raise e

     # Handle the event
    if event['type'] == 'payment_intent.succeeded':
      payment_intent = event['data']['object']
      print(payment_intent)
    # ... handle other event types
    else:
      print('Unhandled event type {}'.format(event['type']))

    return jsonify(success=True)

@app.route("/handle-subscription-success")
@login_required
def handle_subscription_success():
    print("Handling subscription success")  # Debugging print statement

    # Update user account type to 'pro'
    current_user.account_type = "pro"
    db.session.commit()

    return redirect(url_for("index"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure all tables are created
    app.run(debug=True)