from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal
from pathlib import Path
from pydantic import SecretStr, EmailStr


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file = Path(__file__).resolve().parent.parent.parent /'.env',
        env_file_encoding = 'utf-8'
    )
    """Application environment.

    The previous default value was ``"development"`` which was not one of the
    allowed literals (``"dev"``, ``"staging"`` or ``"production"``).  This caused
    ``pydantic`` to raise a validation error during settings initialisation and
    prevented the application and tests from starting.  Using ``"dev"`` keeps the
    intention of a development environment while matching the permitted values.
    """
    env: Literal["dev", "staging", "production"] = "dev"
    debug: bool = True

    azure_vision_key: str = 'azure_vision_key'
    azure_vision_endpoint: str = 'azure_vision_endpoint'

    # Database connection defaults.  The previous placeholders prevented
    # SQLAlchemy from even parsing the connection URL (for instance the port was
    # non-numeric and the password contained angle brackets).  Using sensible
    # dummy values keeps the configuration optional while allowing the engine to
    # be initialised during tests.
    postgres_user: str = 'pg_user'
    postgres_password: str = 'pg_password'
    postgres_host: str = 'pg_host'
    postgres_port: int = 5432
    postgres_dbname: str = 'pg_dbname'
    postgres_timeout: int = 5

    # DigitalOcean Spaces (S3 compatible) configuration.  Provide benign defaults
    # so that the storage client can be constructed in tests without contacting
    # the network or failing validation.
    do_spaces_key: str = 'do_space_key'
    do_spaces_secret: str = 'do_space_secret'
    do_spaces_region: str = 'us-east-1'
    do_spaces_bucket: str = 'do_space_bucket'
    do_spaces_endpoint: str = 'https://example.com'

    # email related
    mail_verify_base_url: str = 'mail-verify-base-url'
    mail_username: str = "mail_username"
    mail_password: SecretStr = "mail_password"
    # ``EmailStr`` requires a valid e‑mail address.  The previous placeholder
    # lacked an ``@`` and failed validation which also stopped the application
    # from starting.  A syntactically valid example address avoids that issue
    # while remaining obviously a placeholder.
    mail_from: EmailStr = "noreply@example.com"
    mail_server: str = "mail_server"
    mail_port: int = 587
    mail_starttls: bool = True
    mail_ssl_tls: bool = False
    use_credentials: bool = True
    validate_certs: bool = True

    mail_token_secret_key: str = "my-personal-email"
    mail_token_algorithm: str = "HS256"
    mail_token_expire_hours: int = 24


# Singleton-style settings object
settings = Settings()