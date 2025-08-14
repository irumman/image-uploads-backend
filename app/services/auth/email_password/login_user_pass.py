from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from fastapi import Depends, HTTPException
from pydantic import EmailStr
from starlette import status

from app.db.crud.app_users import AppUserCrud
from app.db.crud.user_sessions import UserSessionCrud
from app.db.pg_engine import get_db_session
from app.services.auth.email_password.schemas import LoginEmailResponse
from app.services.auth.email_password.jwt_helper import jwt_helper


class LoginUserPass:

    def __init__(self, session=Depends(get_db_session)):
        self.session = session

    async def login_with_password(self, email: EmailStr, password: str) -> LoginEmailResponse:
        user = await AppUserCrud(self.session).get_active_user_by_email(email)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")

        if user.password is None or not jwt_helper.verify_password(password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=1400)
        await UserSessionCrud(self.session).create_session(
            user_id=user.id, token_hash=token_hash, expires_at=expires_at
        )
        resp = LoginEmailResponse(
            access_token=raw_token, token_type="bearer", message="Login successful"
        )
        return resp
