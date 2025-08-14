from __future__ import annotations

from datetime import datetime, timezone
import hashlib

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud.user_sessions import UserSessionCrud
from app.db.models.user_sessions import UserSession
from app.db.models.app_users import AppUser
from app.db.pg_dml import get_by_id
from app.db.pg_engine import get_db_session

security = HTTPBearer()


async def get_current_session(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_db_session),
) -> UserSession:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Not authenticated")
    token_hash = hashlib.sha256(credentials.credentials.encode()).hexdigest()
    user_session = await UserSessionCrud(session).get_session(token_hash)
    now = datetime.now(timezone.utc)
    if (
        user_session is None
        or user_session.revoked
        or user_session.expires_at < now
    ):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user_session


async def get_current_user(
    user_session: UserSession = Depends(get_current_session),
    session: AsyncSession = Depends(get_db_session),
) -> AppUser:
    user = await get_by_id(session, AppUser, user_session.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user
