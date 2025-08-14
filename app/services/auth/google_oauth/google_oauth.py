# user_registration/oauth.py
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

# loads GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET from .env or env vars
config = Config(".env")
oauth = OAuth(config)
oauth.register(
    name="google",
    client_id=config("GOOGLE_CLIENT_ID"),
    client_secret=config("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)