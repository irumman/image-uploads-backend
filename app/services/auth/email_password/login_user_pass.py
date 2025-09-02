# app/services/auth/email_password/service.py
from typing import Literal, Optional
from fastapi import HTTPException, Request
from pydantic import EmailStr
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.jwt_helper import jwt_helper
from app.configs.settings import settings
from app.db.crud.app_users import AppUserCrud
from app.db.models.app_users import AppUser
from app.services.auth.email_password.schemas import LoginEmailResponse
from app.db.crud.auth_sessions import AuthSessionCRUD

REFRESH_COOKIE = "rt"

class LoginUserPass:
    """
    Handles email+password login. Issues access+refresh token_utils and persists the refresh session.
    NOTE: Do NOT use Depends(...) in __init__. Inject dependencies from the route/method call.
    """
    def __init__(self, db: AsyncSession, email: EmailStr, password: str):
        self.db = db
        self.email = email
        self.password = password
        self.refresh_days = 60

    async def _user_password_validate(self) -> AppUser:
        user = await AppUserCrud(self.db).get_active_user_by_email(self.email)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")
        if user.password is None or not jwt_helper.verify_password(self.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return user

    async def login_with_password(self, request: Request) -> LoginEmailResponse:
        user: AppUser = await self._user_password_validate()

        # 1) Refresh token (opaque) + persist session (hash only)
        refresh_raw = jwt_helper.make_refresh_token()
        session_crud = AuthSessionCRUD()
        session = await session_crud.create(
            self.db,
            user_id=user.id,
            refresh_token_raw=refresh_raw,
            ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            device_name=None,
            days=self.refresh_days,
        )

        # 2) Access token (short-lived) with session and user identifiers in the `sub` claim
        sub_payload = {"user_id": user.id, "session_id": str(session.id)}
        access_token = jwt_helper.create_access_token(
            sub=sub_payload,
            secret=
                jwt_helper.access_secret_key
                if hasattr(jwt_helper, "access_secret_key")
                else jwt_helper.secret_key,
            expires_minutes=settings.session_ttl_minutes,
        )

        return LoginEmailResponse(
            user_id=user.id,
            user_name=user.name,
            user_email=user.email,
            access_token=access_token,
            refresh_token=refresh_raw,
            message="Login successful",
        )

