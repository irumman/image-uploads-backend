from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
import uuid

from app.core.jwt_helper import jwt_helper
from app.db.pg_engine import get_db_session
from app.db.crud.auth_sessions import AuthSessionCRUD

bearer_scheme = HTTPBearer()


async def auth_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db=Depends(get_db_session),
) -> int:
    """Validate access token and return the authenticated user's ID."""
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, jwt_helper.access_secret_key, algorithms=[jwt_helper.algorithm]
        )
        user_id = int(payload.get("sub"))
        session_id = uuid.UUID(payload.get("session_id"))
    except (JWTError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

    session = await AuthSessionCRUD().get_active_by_id(db, session_id=session_id)
    if session is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id
