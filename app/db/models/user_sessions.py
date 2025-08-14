from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import BigInteger, Boolean, ForeignKey, TIMESTAMP, Text
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

Base = declarative_base()


class UserSession(Base):
    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("app_users.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(Text, unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
