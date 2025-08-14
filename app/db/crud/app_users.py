from typing import Optional

from pydantic import EmailStr
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.app_users import AppUser
from app.db.pg_dml import get_one

class AppUserCrud:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active_user_by_email(self, email: EmailStr) -> Optional[AppUser]:
        result = await get_one(self.session, AppUser, email=email, is_active=True)
        return result

    async def get_inactive_user_by_email(self, email: EmailStr) -> Optional[AppUser]:
        result = await get_one(self.session, AppUser, email=email, is_active=False)
        return result

    async def create(self, **fields) -> AppUser:
        user = AppUser(**fields)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user