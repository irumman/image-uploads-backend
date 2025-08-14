from datetime import datetime, timedelta, timezone
from typing import Any
from app.configs.settings import settings

from jose import jwt
from jose.exceptions import JWTError
from passlib.context import CryptContext

class JwtHelper:
    def __init__(self):
        self.algorithm  = settings.mail_token_algorithm
        self.secret_key = settings.mail_token_secret_key
        self.expire_hours = settings.mail_token_expire_hours
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain: str, hashed: str) -> bool:
        return self.pwd_context.verify(plain, hashed)

    def hash_password(self, plain: str) -> str:
        return self.pwd_context.hash(plain)

    def create_access_token(self, *, sub: str | int, secret: str, expires_minutes: int = 60) -> str:
        now = datetime.now(timezone.utc)
        to_encode: dict[str, Any] = {
            "sub": str(sub),
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
        }
        return jwt.encode(to_encode, secret, algorithm=self.algorithm)

    def create_email_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(tz=timezone.utc) + timedelta(hours=self.expire_hours)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_email_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm, ])
            return payload if "sub" in payload else None
        except JWTError:
            return {}

jwt_helper = JwtHelper()