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
import stripe
from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    jsonify,
    request,
    session,
    flash,
)
from flask_login import current_user, login_user, logout_user, login_required
from database.db_setup import setup_database
from database.models import db, User, FileUpload
from file_handling.file_routes import file_blueprint
from auth.oauth import oauth, configure_oauth
from auth.login_manager import login_manager

app = Flask(__name__)


app.config[
    "STRIPE_PUBLIC_KEY"
] = "pk_test_51OVEkqDAl3fqs0z5WYJHtSc1Jn2WZD4w7vV7rVOULeHvdgYSoXxa415eCxTnYBZ0xTXCqDBdW5xla4hw1xyjumQQ00T45kDMNP"
app.config[
    "STRIPE_SECRET_KEY"
] = "sk_test_51OVEkqDAl3fqs0z5tlfYXaUWj8cLjU8eMHhEp4xgxjdt5IbVxv4Mh7qJzkiul1XRVflXNX79Q4zNfjnVacLeje8s00usdgCVQf"
endpoint_secret = "whsec_95ko9Dz5I1d9tNBOUyrzT89hp3ujpLcn"
Domain = "http://localhost:5000"
stripe.api_key = "sk_test_51OVEkqDAl3fqs0z5tlfYXaUWj8cLjU8eMHhEp4xgxjdt5IbVxv4Mh7qJzkiul1XRVflXNX79Q4zNfjnVacLeje8s00usdgCVQf"

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://eugene:eugene@localhost/doc_grammar"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Suppress a warning
app.config["SECRET_KEY"] = "eugene_secret"  # Flash messages

if not os.path.exists("file_uploads"):
    os.makedirs("file_uploads")

app.config["UPLOAD_FOLDER"] = "file_uploads"
stripe.api_key = app.config["STRIPE_SECRET_KEY"]

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

        subscription_type = request.form.get("subscription_type", "basic")
        price_id = "price_1OVuXjDAl3fqs0z5yCreg4ui"  # default to basic price
        if subscription_type == "pro":
            price_id = "price_1OVuakDAl3fqs0z5AzKRagmB"  # pro price
            # current_user.account_type = "Premium"
        elif subscription_type == "basic":
            price_id = "price_1OW13EDAl3fqs0z5tvO7wIZF"  # basic price
            # current_user.account_type = "Basic"
        # db.session.commit()

        # Create a customer in Stripe
        customer = stripe.Customer.create(
            email=current_user.email,  # use the current user's email
            # add any other customer details you need
        )

        # Store the Stripe customer ID in your database
        current_user.stripe_customer_id = customer.id
        db.session.commit()

        try:
            # Create a checkout session
            checkout_session = stripe.checkout.Session.create(
                customer=customer.id,
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                mode="subscription",
                success_url=url_for("index", _external=True)
                + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=url_for("index", _external=True),
                metadata={
                    "subscription_type": subscription_type,
                    "user_id": current_user.id,  # Store the user ID to find the user in the webhook
                },
            )

            print(
                f"Checkout session created: {checkout_session.id}"
            )  # Debugging print statement

            # Redirect to the checkout session
            return redirect(checkout_session.url, code=303)
        except stripe.error.StripeError as e:
            app.logger.error(f"Stripe error: {str(e)}")
            print(f"Stripe error: {str(e)}")  # Debugging print statement
            return jsonify(error=str(e)), 403

    print("Handling a GET request")  # Debugging print statement

    # If it's a GET request, return the main page with the Stripe public key
    return render_template(
        "index.html", stripe_public_key=app.config["STRIPE_PUBLIC_KEY"]
    )


@app.route("/webhook", methods=["POST"])
def webhook():
    print("webhook called")
    event = None
    payload = request.data
    sig_header = request.headers["STRIPE_SIGNATURE"]

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        # Invalid payload
        print("Invalid payload")
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print("Invalid signature")
        raise e

    # Handle the event
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        print(payment_intent)
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        line_items = stripe.checkout.Session.list_line_items(session["id"], limit=1)
        customer_email = session["customer_details"]["email"]
        customer_name = session["customer_details"]["name"]
        customer_id = session["customer"]
        subscription_type = session["metadata"]["subscription_type"]
        product_des = line_items["data"][0]["description"]
        user_id = session["metadata"]["user_id"]
        print(customer_name)
        print(line_items["data"][0]["description"])
        print(customer_email)
        print(customer_id)
        subscription_purchased = True
        #   user = User.query.filter_by(email=customer_email).first()
        #   if user:
        #     user.stripe_customer_id = session['customer']
        #     if product_des == "Premium":
        #         user.account_type = "Premium"
        #     elif product_des == "Basic":
        #         user.account_type = "Basic"
        #     elif product_des == "Free":
        #         user.account_type = "Free"
        #     db.session.commit()
        #     return render_template("index.html", subscription_purchased=True)
        #   else:
        #     print("User not found")
        # Find the user in your database
        user = User.query.get(user_id)
        if user:
            # Update the user account type
            if subscription_type == "pro":
                user.account_type = "Premium"
            elif subscription_type == "basic":
                user.account_type = "Basic"
            user.subscription_purchased = True
            db.session.commit()

            print("Payment succeeded!")
        print(subscription_purchased)
    # Handle the event
    # https://stripe.com/docs/customer-management/integrate-customer-portal
    if event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]
        # https://stripe.com/docs/api/subscriptions/object
        new_plan = subscription["items"]["data"][0]["plan"]["id"]
        cancel_at_period_end = subscription["cancel_at_period_end"]
        print(new_plan)
        print(cancel_at_period_end)

        # Find the user with the given Stripe customer ID
        # https://stripe.com/docs/api/pagination
        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        if user:
            if cancel_at_period_end == True:
                user.account_type = "Free"
            elif new_plan == "price_1OVuakDAl3fqs0z5AzKRagmB":
                user.account_type = "Premium"
            elif new_plan == "price_1OW13EDAl3fqs0z5tvO7wIZF":
                user.account_type = "Basic"
            elif new_plan == "price_1OVuXjDAl3fqs0z5yCreg4ui":
                user.account_type = "Free"
            print("Updated account type:", user.account_type)
            db.session.commit()
        else:
            print("User not found")
    if event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]
        print("Subscription cancelled")

        # Find the user with the given Stripe customer ID
        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        if user:
            # Update the user's account type to Free
            user.account_type = "Free"
            db.session.commit()
        else:
            print("User not found")

    # ... handle other event types
    else:
        print("Unhandled event type {}".format(event["type"]))
    return jsonify(success=True)


@app.route("/handle-subscription-success")
@login_required
def handle_subscription_success():
    print("Handling subscription success")  # Debugging print statement

    # Update user account type to 'pro'
    current_user.account_type = "Premium"
    db.session.commit()

    # return render_template("index.html", subscription_purchased=True)
    return redirect(url_for("index"))


def premium_user_required(func):
    """
    Decorator to check if the user has a "Premium" account type.
    If not, flashes an error message and redirects to the homepage.
    """

    def wrapper(*args, **kwargs):
        if current_user.account_type != "Premium":
            flash("Only Premium users are allowed to perform this action.", "error")
            return redirect(url_for("index"))
        return func(*args, **kwargs)

    return wrapper


@app.route("/create-customer-portal-session", methods=["GET", "POST"])
@login_required
def create_customer_portal_session():
    try:
        # Create a customer portal session
        portal_session = stripe.billing_portal.Session.create(
            customer=current_user.stripe_customer_id,
            return_url=url_for("index", _external=True),
        )

        print(f"Portal session created: {portal_session.id}")

        # Redirect to the customer portal session
        return redirect(portal_session.url)
    except stripe.error.StripeError as e:
        app.logger.error(f"Stripe error: {str(e)}")
        print(f"Stripe error: {str(e)}")
        return jsonify(error=str(e)), 403


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure all tables are created
    app.run(debug=True)


# @app.route("/check_db")
# def check_database_connection():
#     try:
#         db.session.query(FileUpload).first()
#         return "Database connection successful. Happy coding"
#     except Exception as e:
#         return f"Database connection error: {str(e)}"
