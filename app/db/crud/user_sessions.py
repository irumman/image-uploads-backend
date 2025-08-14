from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user_sessions import UserSession
from app.db.pg_dml import insert_record, get_by_id


class UserSessionCrud:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_session(
        self, user_id: int, token_hash: str, expires_at: datetime
    ) -> UserSession:
        session_obj = UserSession(
            user_id=user_id, token_hash=token_hash, expires_at=expires_at
        )
        return await insert_record(self.session, session_obj)

    async def get_session(self, token_hash: str) -> Optional[UserSession]:
        stmt = select(UserSession).where(UserSession.token_hash == token_hash)
        result = await self.session.execute(stmt.limit(1))
        return result.scalars().first()

    async def revoke_session(self, session_id: int) -> None:
        session_obj = await get_by_id(self.session, UserSession, session_id)
        if session_obj is None:
            return
        session_obj.revoked = True
        await self.session.commit()
