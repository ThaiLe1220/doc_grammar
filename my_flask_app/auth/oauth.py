""" Filename: oauth.py - Directory: my_flask_app/auth 
"""
import os
from authlib.integrations.flask_client import OAuth

oauth = OAuth()


def configure_oauth(app):
    oauth.init_app(app)
    oauth.register(
        name="google",
        client_id=os.environ.get("OAUTH_CLIENT_ID"),
        client_secret=os.environ.get("OAUTH_CLIENT_SECRET"),
        access_token_url="https://oauth2.googleapis.com/token",
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        api_base_url="https://www.googleapis.com/oauth2/v1/",
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )
