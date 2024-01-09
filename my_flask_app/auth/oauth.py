""" Filename: oauth.py - Directory: my_flask_app/auth 

This module configures OAuth for a Flask application using Authlib. It initializes
the OAuth object with the application context and registers the Google OAuth client
with necessary details such as client ID, client secret, and various URLs required
for the OAuth flow.

"""
from authlib.integrations.flask_client import OAuth

oauth = OAuth()


def configure_oauth(app):
    """
    Configures OAuth for the Flask application using Authlib.

    This function initializes the OAuth object with the application context and
    registers the Google OAuth client with necessary details such as client ID,
    client secret, and various URLs required for the OAuth flow.

    Args:
        app (Flask): The Flask application instance to configure with OAuth.
    """
    oauth.init_app(app)
    oauth.register(
        name="google",
        client_id="683306391910-u0auqkk6t35664l17ai0q2camp5p22rf.apps.googleusercontent.com",
        client_secret="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",
        access_token_url="https://oauth2.googleapis.com/token",
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        api_base_url="https://www.googleapis.com/oauth2/v1/",
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )
    # oauth.register(
    #     name="google",
    #     server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    #     client_kwargs={"scope": "openid email profile"},
    #     client_id="1020591203255-is6vclts4048a4m48bhq5djb4am0n0d7.apps.googleusercontent.com",
    #     client_secret="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",
    #     access_token_url="https://accounts.google.com/o/oauth2/token",
    #     access_token_params=None,
    #     authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
    #     authorize_params=None,
    #     api_base_url="https://www.googleapis.com/oauth2/v1/",
    #     userinfo_endpoint="https://openidconnect.googleapis.com/v1/userinfo",
    #     jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
    #     revocation_endpoint="https://oauth2.googleapis.com/revoke",
    # )
