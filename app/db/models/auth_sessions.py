from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from sqlalchemy import ForeignKey, BigInteger, TIMESTAMP
from sqlalchemy.dialects.postgresql import INET, UUID, BYTEA
import uuid

Base = declarative_base()

class AuthSessions(Base):
    __tablename__ = "auth_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    refresh_hash: Mapped[bytes] = mapped_column(BYTEA, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    expires_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    ip: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(nullable=True)
    device_name: Mapped[Optional[str]] = mapped_column(nullable=True)
    is_revoked: Mapped[bool] = mapped_column(default=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    revoke_reason: Mapped[Optional[str]] = mapped_column(nullable=True)
    replaced_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)

    @staticmethod
    def default_expiry(days: int = 30) -> datetime:
        return datetime.now(timezone.utc) + timedelta(days=days)
