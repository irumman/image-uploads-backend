from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.configs.constants import ProcessingStatus
from app.db.models.image_uploads import ImageUploads
from app.db.pg_dml import insert_record, get_many


class ImageUploadCRUD:
    """CRUD helper for :class:`ImageUploads`."""

    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        file_path: str,
        chapter: int,
        line_start: int,
        line_end: int,
        script_id: int | None = None,
        status: int = ProcessingStatus.UPLOADED,
        upload_timestamp: datetime | None = None,
    ) -> ImageUploads:
        """Insert a new ``ImageUploads`` row."""
        row = ImageUploads(
            user_id=user_id,
            file_path=file_path,
            chapter=chapter,
            line_start=line_start,
            line_end=line_end,
            status=status,
            script_id=script_id,
            upload_timestamp=upload_timestamp or datetime.now(timezone.utc),
        )
        return await insert_record(db, row)

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> list[ImageUploads]:
        """Fetch all uploads for a given user."""
        return await get_many(db, ImageUploads, filters={"user_id": user_id})
