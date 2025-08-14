from fastapi_mail import ConnectionConfig
from app.configs.settings import settings

class EmailConfigs:
    def __init__(self):
        self.mail_verify_base_url = settings.mail_verify_base_url
        self.mail_token_secret_key = settings.mail_token_secret_key
        self.mail_token_algorithm = settings.mail_token_algorithm
        self.mail_token_expire_hours = settings.mail_token_expire_hours

        self.smtp_conf = ConnectionConfig(
            MAIL_USERNAME = settings.mail_username,
            MAIL_PASSWORD = settings.mail_password,
            MAIL_FROM = settings.mail_from,
            MAIL_SERVER = settings.mail_server,
            MAIL_PORT = settings.mail_port,
            MAIL_STARTTLS = settings.mail_starttls,
            MAIL_SSL_TLS = settings.mail_ssl_tls,
            USE_CREDENTIALS = settings.use_credentials,
            VALIDATE_CERTS = settings.validate_certs
        )

email_conf = EmailConfigs()