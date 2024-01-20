""" Filename: app.py - Directory: my_flask_app 
"""
import datetime
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
)

from flask_login import current_user, login_user, logout_user, login_required
from database.db_setup import setup_database
from database.models import db, User, FileUpload
from file_handling.file_routes import file_blueprint
from auth.oauth import oauth, configure_oauth
from auth.login_manager import login_manager

app = Flask(__name__)
print("App initialized.")

# setting up stripe api keys
app.config[
    "STRIPE_PUBLIC_KEY"
] = "pk_test_51OVEkqDAl3fqs0z5WYJHtSc1Jn2WZD4w7vV7rVOULeHvdgYSoXxa415eCxTnYBZ0xTXCqDBdW5xla4hw1xyjumQQ00T45kDMNP"
app.config[
    "STRIPE_SECRET_KEY"
] = "sk_test_51OVEkqDAl3fqs0z5tlfYXaUWj8cLjU8eMHhEp4xgxjdt5IbVxv4Mh7qJzkiul1XRVflXNX79Q4zNfjnVacLeje8s00usdgCVQf"
endpoint_secret = "whsec_pXA4oZ40ktdIpfYtJmlX3Z9LmI5v19VZ"
Domain = "http://localhost:5000"
stripe.api_key = "sk_test_51OVEkqDAl3fqs0z5tlfYXaUWj8cLjU8eMHhEp4xgxjdt5IbVxv4Mh7qJzkiul1XRVflXNX79Q4zNfjnVacLeje8s00usdgCVQf"

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://huyhua:namhuy1211@localhost/doc_grammar"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Suppress a warning
app.config["SECRET_KEY"] = "eugene_secret"  # Flash messages

if not os.path.exists("file_uploads"):
    os.makedirs("file_uploads")

app.config["UPLOAD_FOLDER"] = "file_uploads"
stripe.api_key = app.config["STRIPE_SECRET_KEY"]

from flask_migrate import Migrate

migrate = Migrate(app, db)

setup_database(app)
print("Database setup completed.")

configure_oauth(app)
print("OAuth configured.")

login_manager.init_app(app)
print("Login manager initialized.")

app.register_blueprint(file_blueprint, url_prefix="/files")
print("Blueprint for file handling registered.")


@app.route("/")
def landing_page():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    # If user is not authenticated, show the landing page
    print("Landing page accessed.")
    return render_template("landing-page.html")


@app.route("/index")
def index():
    page = request.args.get("page", 1, type=int)
    per_page = 5  # Items per page
    sort_by = request.args.get("sort", "time")
    descending = request.args.get("descending", "false").lower() == "true"

    # Get search term from query string
    search_term = request.args.get("search", "")

    # Start with a query that selects all files
    file_query = FileUpload.query.filter_by(user_id=current_user.id)

    # Apply search filter if a search term is provided
    if search_term:
        file_query = file_query.filter(FileUpload.file_name.ilike(f"%{search_term}%"))

    # Determine the sort order
    if sort_by == "time":
        order = FileUpload.upload_time.desc() if descending else FileUpload.upload_time
    elif sort_by == "name":
        order = FileUpload.file_name.desc() if descending else FileUpload.file_name
    elif sort_by == "size":
        order = FileUpload.file_size.desc() if descending else FileUpload.file_size
    else:
        order = FileUpload.upload_time  # Default sort

    # Apply sorting before pagination
    files_query = file_query.order_by(order)
    files_pagination = files_query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    files = files_pagination.items
    total_pages = (
        files_pagination.pages if files_pagination.pages is not None else 1
    )  # Total number of pages

    file_id = session.get("file_id")
    corrections = None

    if file_id:
        file = FileUpload.query.get(file_id)
        if file:
            corrections = file.corrections

    # Pass the necessary variables to the template
    return render_template(
        "index.html",
        files=files,
        total_pages=total_pages,
        current_user=current_user,
        corrections=corrections,
        current_page=page,
        sort=sort_by,
        descending=descending,
        search_term=search_term,  # Pass the search term back to the template
    )


@app.route("/login")
def login():
    nonce = secrets.token_urlsafe()
    session["nonce"] = nonce
    redirect_uri = url_for("authorize", _external=True)
    return oauth.google.authorize_redirect(redirect_uri, nonce=nonce)


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
    print("User logged in", user)
    return redirect("/index")


@login_manager.user_loader
def load_user(user_id):
    print("Load user", user_id)
    return User.query.get(int(user_id))


@app.route("/logout")
@login_required
def logout():
    # Clear the session
    session["file_id"] = None

    logout_user()
    print("User logged out")
    return redirect(url_for("landing_page"))


@app.route("/billing-plan")
def billing_plan():
    print("Go to  billing plan")
    return render_template("billing-plan.html")


@app.route("/subscribe", methods=["GET", "POST"])
@login_required
def subscribe():
    print("Entered the /subscribe route")

    if request.method == "POST":
        print("Handling a POST request")

        subscription_type = request.form.get("subscription_type", "basic")
        price_id = "price_1OVuXjDAl3fqs0z5yCreg4ui"  # default to basic price
        if subscription_type == "pro":
            price_id = "price_1OVuakDAl3fqs0z5AzKRagmB"  # pro price
        elif subscription_type == "basic":
            price_id = "price_1OW13EDAl3fqs0z5tvO7wIZF"  # basic price

        # Create a customer in Stripe
        customer = stripe.Customer.create(
            email=current_user.email,  # use the current user's email
        )

        current_user.stripe_customer_id = customer.id
        db.session.commit()

        try:
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
                    "user_id": current_user.id,
                },
            )

            print(f"Checkout session created: {checkout_session.id}")

            return redirect(checkout_session.url, code=303)
        except stripe.error.StripeError as e:
            app.logger.error(f"Stripe error: {str(e)}")
            print(f"Stripe error: {str(e)}")
            return jsonify(error=str(e)), 403

    print("Handling a GET request")

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
        user = User.query.get(user_id)
        if user:
            if subscription_type == "pro":
                user.account_type = "Premium"
            elif subscription_type == "basic":
                user.account_type = "Basic"
            user.subscription_purchased = True
            db.session.commit()

            print("Payment succeeded!")
        print(subscription_purchased)

    # https://stripe.com/docs/customer-management/integrate-customer-portal
    if event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]
        # https://stripe.com/docs/api/subscriptions/object
        new_plan = subscription["items"]["data"][0]["plan"]["id"]
        cancel_at_period_end = subscription["cancel_at_period_end"]
        # Get the expiration date of the current subscription
        expiration_date = datetime.datetime.fromtimestamp(
            subscription["current_period_end"]
        )

        print("Expiration date:", expiration_date)
        print(new_plan)
        print(cancel_at_period_end)

        # Find the user with the given Stripe customer ID
        # https://stripe.com/docs/api/pagination
        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        if user:
            if cancel_at_period_end == True:
                user.account_type = "Free"
                user.subscription_purchased = False
                user.expired_date = None
            elif new_plan == "price_1OVuakDAl3fqs0z5AzKRagmB":
                user.account_type = "Premium"
                user.expired_date = expiration_date
            elif new_plan == "price_1OW13EDAl3fqs0z5tvO7wIZF":
                user.account_type = "Basic"
                user.expired_date = expiration_date
            elif new_plan == "price_1OVuXjDAl3fqs0z5yCreg4ui":
                user.account_type = "Free"
                user.subscription_purchased = False
                user.expired_date = expiration_date
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


@app.route("/create-customer-portal-session", methods=["GET", "POST"])
@login_required
def create_customer_portal_session():
    print("Create customer portal session")
    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=current_user.stripe_customer_id,
            return_url=url_for("index", _external=True),
        )

        print(f"Portal session created: {portal_session.id}")

        return redirect(portal_session.url)
    except stripe.error.StripeError as e:
        app.logger.error(f"Stripe error: {str(e)}")
        print(f"Stripe error: {str(e)}")
        return jsonify(error=str(e)), 403


@app.route("/handle-subscription-success")
@login_required
def handle_subscription_success():
    print("Handling subscription success")

    current_user.account_type = "Premium"
    db.session.commit()

    return redirect(url_for("index"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("All database tables created.")
    app.run(debug=True)
    print("App running in debug mode.")
