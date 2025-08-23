from fastapi import HTTPException
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud.auth_sessions import AuthSessionCRUD
from app.services.auth.email_password.schemas import LogoutResponse


class Logout:
    """Handle revoking a refresh token for logout."""

    def __init__(self, db: AsyncSession, user_id: int, refresh_token: str):
        self.db = db
        self.user_id = user_id
        self.refresh_token = refresh_token
        self.session_crud = AuthSessionCRUD()

    async def logout(self) -> LogoutResponse:
        session = await self.session_crud.find_valid_by_token(
            self.db,
            user_id=self.user_id,
            refresh_token_raw=self.refresh_token,
        )
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session",
            )
        await self.session_crud.revoke(self.db, session_id=session.id, reason="logout")
        return LogoutResponse(message="Logout successful")
