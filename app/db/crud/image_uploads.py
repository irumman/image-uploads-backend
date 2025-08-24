from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.image_uploads import ImageUploads
from app.db.pg_dml import get_many


class ImageUploadCrud:
    """CRUD helper for ``ImageUploads`` records."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_script(self, script_id: int) -> Sequence[ImageUploads]:
        """Return all uploads associated with a ``script_id``."""
        return await get_many(self.session, ImageUploads, filters={"script_id": script_id})

