from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.core.jwt_helper import jwt_helper

bearer_scheme = HTTPBearer()

async def auth_dependency(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> int:
    """Validate access token and return the authenticated user's ID."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, jwt_helper.access_secret_key, algorithms=[jwt_helper.algorithm])
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id
