""" Filename: oauth.py - Directory: my_flask_app/auth 
"""
from authlib.integrations.flask_client import OAuth

oauth = OAuth()


def configure_oauth(app):
    oauth.init_app(app)
    oauth.register(
        name="google",
        client_id="1020591203255-is6vclts4048a4m48bhq5djb4am0n0d7.apps.googleusercontent.com",
        client_secret="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",
        access_token_url="https://accounts.google.com/o/oauth2/token",
        access_token_params=None,
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        authorize_params=None,
        api_base_url="https://www.googleapis.com/oauth2/v1/",
        client_kwargs={"scope": "openid profile email"},
    )
