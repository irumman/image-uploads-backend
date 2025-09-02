import os
import secrets
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import jwt
from jose.exceptions import JWTError
from passlib.context import CryptContext

from app.configs.settings import settings


class JwtHelper:
    """
    Unified helper for:
      - password hashing & verification (bcrypt via passlib)
      - access token (JWT) creation
      - email token (JWT) creation/verification
      - refresh token utilities (opaque token generate + hash + constant-time compare)

    Backwards compatible with your previous JwtHelper methods.
    """

    def __init__(self):
        self.algorithm: str = settings.mail_token_algorithm

        # Secrets:
        # - Email/JWT secret (existing)
        self.secret_key: str = settings.mail_token_secret_key
        self.access_secret_key: str = settings.access_token_secret_key
        self.expire_hours: int = settings.mail_token_expire_hours

        # Password hashing
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        # Refresh-token helpers
        # A server-side “pepper” that never goes to the DB (defense-in-depth)
        self.refresh_token_pepper: str = settings.refresh_token_pepper
        # Token size in bytes before urlsafe encoding (48 ≈ ~64 chars)
        self.refresh_token_bytes: int = settings.refresh_token_bytes

    # -------------------------
    # Passwords (unchanged API)
    # -------------------------
    def verify_password(self, plain: str, hashed: str) -> bool:
        return self.pwd_context.verify(plain, hashed)

    def hash_password(self, plain: str) -> str:
        return self.pwd_context.hash(plain)

    # -------------------------
    # Access token_utils (JWT)
    # -------------------------
    def create_access_token(
        self,
        *,
        sub: str | int | dict[str, Any],
        secret: Optional[str] = None,
        expires_minutes: int = 60,
        extra_claims: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        Create a short-lived JWT access token.
        - If `secret` not provided, uses settings.access_token_secret_key (or falls back to mail_token_secret_key).
        - `extra_claims` lets you add roles, scopes, etc.
        """
        now = datetime.now(timezone.utc)
        # `sub` must be a string per JWT spec. Allow dicts by JSON-encoding them.
        if isinstance(sub, (dict, list)):
            payload_sub = json.dumps(sub)
        else:
            payload_sub = str(sub)
        payload: dict[str, Any] = {
            "sub": payload_sub,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
        }
        if extra_claims:
            payload.update(extra_claims)
        use_secret = secret or self.access_secret_key
        return jwt.encode(payload, use_secret, algorithm=self.algorithm)

    # -------------------------
    # Email token_utils (JWT)
    # -------------------------
    def create_email_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(tz=timezone.utc) + timedelta(hours=self.expire_hours)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_email_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload if "sub" in payload else None
        except JWTError:
            return {}

    # -------------------------
    # Refresh token_utils (opaque)
    # -------------------------
    def make_refresh_token(self) -> str:
        """
        Generate a high-entropy opaque token to set in an HttpOnly cookie.
        The raw value is NEVER stored in the DB—only its hash.
        """
        return secrets.token_urlsafe(self.refresh_token_bytes)

    def hash_refresh(self, token: str) -> bytes:
        """
        Hash a refresh token with SHA-256 and a server-side pepper.
        Store the resulting bytes in the DB (e.g., BYTEA).
        """
        h = hashlib.sha256()
        if self.refresh_token_pepper:
            h.update(self.refresh_token_pepper.encode("utf-8"))
        h.update(token.encode("utf-8"))
        return h.digest()

    @staticmethod
    def constant_time_eq(a: bytes, b: bytes) -> bool:
        """
        Constant-time comparison to avoid timing side-channels.
        """
        return hmac.compare_digest(a, b)


jwt_helper = JwtHelper()
