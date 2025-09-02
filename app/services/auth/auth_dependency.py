from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
import uuid
import json
from typing import Any

from app.core.jwt_helper import jwt_helper
from app.db.pg_engine import get_db_session
from app.db.crud.auth_sessions import AuthSessionCRUD

bearer_scheme = HTTPBearer()

async def auth_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db=Depends(get_db_session),
) -> dict[str, Any]:
    """Validate access token and return user and session identifiers."""
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, jwt_helper.access_secret_key, algorithms=[jwt_helper.algorithm]
        )
        sub_raw = payload.get("sub") or "{}"
        sub_payload = json.loads(sub_raw)
        user_id = int(sub_payload.get("user_id"))
        session_id = uuid.UUID(sub_payload.get("session_id"))
    except (JWTError, TypeError, ValueError, AttributeError, json.JSONDecodeError):
        raise HTTPException(status_code=401, detail="Invalid token")

    session = await AuthSessionCRUD().get_active_by_id(db, session_id=session_id)
    if session is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"user_id": user_id, "session_id": session_id}
