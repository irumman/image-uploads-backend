from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.configs.constants import ProcessingStatus
from app.db.models.image_uploads import ImageUploads
from app.db.pg_dml import insert_record


class ImageUploadCRUD:
    """CRUD helper for :class:`ImageUploads`."""

    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        file_path: str,
        chapter: int,
        ayat_start: int,
        ayat_end: int,
        script_id: int | None = None,
        status: int = ProcessingStatus.UPLOADED,
        upload_timestamp: datetime | None = None,
    ) -> ImageUploads:
        """Insert a new ``ImageUploads`` row."""
        row = ImageUploads(
            user_id=user_id,
            file_path=file_path,
            chapter=chapter,
            ayat_start=ayat_start,
            ayat_end=ayat_end,
            status=status,
            script_id=script_id,
            upload_timestamp=upload_timestamp or datetime.now(timezone.utc),
        )
        return await insert_record(db, row)
