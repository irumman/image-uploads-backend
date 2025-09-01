from datetime import datetime, timezone
from typing import Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.jwt_helper import JwtHelper
from app.db.models.auth_sessions import AuthSessions

from app.db.pg_dml import  (
    insert_record,
    upsert_record,
    get_by_id,
    get_many,
)

class AuthSessionCRUD:
    """
    CRUD for AuthSession that delegates to shared pg_dml helpers.
    """
    def __init__(self):
        self.token_utils = JwtHelper()

    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        refresh_token_raw: str,
        ip: Optional[str],
        user_agent: Optional[str],
        device_name: Optional[str] = None,
        days: int = 30,
    ) -> AuthSessions:
        row = AuthSessions(
            user_id=user_id,
            refresh_hash=self.token_utils.hash_refresh(refresh_token_raw),
            created_at=datetime.now(timezone.utc),
            expires_at=AuthSessions.default_expiry(days),
            ip=ip,
            user_agent=user_agent,
            device_name=device_name,
        )
        return await insert_record(db, row)

    async def find_valid_by_token(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        refresh_token_raw: str,
        window_limit: int = 50,  # cap to keep the in-Python hash check small
    ) -> Optional[AuthSessions]:
        """
        We use get_many() for equality filters and ordering. Since your pg_dml
        helper doesn't do range predicates, we filter `expires_at > now()` in Python.
        """
        # equality filters done in SQL
        rows: list[AuthSessions] = await get_many(
            db,
            AuthSessions,
            filters={"user_id": user_id, "is_revoked": False},
            order_by=[AuthSessions.created_at.desc()],
            limit=window_limit,
            offset=None,
        )
        # additional constraints in Python
        now = datetime.now(timezone.utc)
        probe = self.token_utils.hash_refresh(refresh_token_raw)

        for r in rows:
            if r.expires_at > now and self. token_utils.constant_time_eq(r.refresh_hash, probe):
                return r
        return None

    async def get_active_by_id(
        self,
        db: AsyncSession,
        *,
        session_id: uuid.UUID,
    ) -> Optional[AuthSessions]:
        row = await get_by_id(db, AuthSessions, session_id)
        if not row:
            return None
        now = datetime.now(timezone.utc)
        if row.is_revoked or row.expires_at <= now:
            return None
        return row

    async def revoke(
        self,
        db: AsyncSession,
        *,
        session_id: uuid.UUID,
        reason: Optional[str] = None,
    ) -> None:
        row = await get_by_id(db, AuthSessions, session_id)
        if not row:
            return
        row.is_revoked = True
        row.revoked_at = datetime.utcnow()
        row.revoke_reason = reason
        await upsert_record(db, row)

    async def touch(self, db: AsyncSession, *, session_id: uuid.UUID) -> None:
        row = await get_by_id(db, AuthSessions, session_id)
        if not row:
            return
        row.last_seen_at = datetime.utcnow()
        await upsert_record(db, row)

    async def link_replacement(
        self,
        db: AsyncSession,
        *,
        old_id: uuid.UUID,
        new_id: uuid.UUID,
    ) -> None:
        row = await get_by_id(db, AuthSessions, old_id)
        if not row:
            return
        row.replaced_by = new_id
        await upsert_record(db, row)

    async def purge_old(
        self,
        db: AsyncSession,
        *,
        # NOTE: pg_dml has no delete helper; keep this simple and conservative:
        # delete only items that are already revoked or expired AND older than `created_before`.
        created_before: Optional[datetime] = None,
    ) -> int:
        """
        Purges in two passes using your helpers, to avoid raw DELETE.
        If you expect millions of rows, replace with a single SQL DELETE.
        """
        now = datetime.utcnow()
        # Pull a reasonable batch and delete via session for safety.
        # (Tune the limit or loop in batches if needed.)
        candidates = await get_many(
            db,
            AuthSessions,
            filters={"is_revoked": True},  # start with revoked
            order_by=[AuthSessions.created_at.asc()],
            limit=500,
        )
        extra = await get_many(
            db,
            AuthSessions,
            filters={"is_revoked": False},  # still active but maybe expired
            order_by=[AuthSessions.created_at.asc()],
            limit=500,
        )
        to_delete: list[AuthSessions] = []
        for r in candidates:
            if (created_before is None or r.created_at < created_before):
                to_delete.append(r)
        for r in extra:
            if r.expires_at < now and (created_before is None or r.created_at < created_before):
                to_delete.append(r)

        # Use the ORM session delete so we stay consistent with your pattern
        # (this is the one place we don't have a pg_dml helper).
        count = 0
        for r in to_delete:
            await db.delete(r)
            count += 1
        if count:
            await db.commit()
        return count
