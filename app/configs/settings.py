from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal
from pathlib import Path
from pydantic import SecretStr, EmailStr


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file = Path(__file__).resolve().parent.parent.parent /'.env',
        env_file_encoding = 'utf-8'
    )
    env: Literal["dev", "staging", "production"] = "development"
    debug: bool = True

    azure_vision_key: str = 'azure_vision_key'
    azure_vision_endpoint: str = 'azure_vision_endpoint'

    postgres_user: str = 'pg_user'
    postgres_password: str = '<PASSWORD>'
    postgres_host: str = 'pg_host'
    postgres_port: str = 'pg_port'
    postgres_dbname: str = 'pg_dbname'
    postgres_timeout: int = 5

    do_spaces_key: str = 'do_space_key'
    do_spaces_secret: str = 'do_space_secret'
    do_spaces_region: str = 'do_space_region'
    do_spaces_bucket: str = 'do_space_bucket'
    do_spaces_endpoint: str = 'do_space_endpoint'

    # email related
    mail_verify_base_url: str = 'mail-verify-base-url'
    mail_username: str = "mail_username"
    mail_password: SecretStr = "mail_password"
    mail_from: EmailStr = "mail_from"
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