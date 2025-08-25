from pathlib import Path
from fastapi import UploadFile, HTTPException

from app.db.pg_engine import sessionmanager
from app.db.crud.image_uploads import ImageUploadCRUD
from app.services.image_uploads.schemas import ImageUploadResponse, ImageUploadRecord
from app.services.storage.do_space import do_space
from app.configs.constants import ProcessingStatus


class UploadService:
    def __init__(self) -> None:
        self.crud = ImageUploadCRUD()

    async def upload_image(
        self,
        file: UploadFile,
        user_id: int,
        chapter: int,
        ayat_start: int,
        ayat_end: int,
        script_id: int
    ) -> ImageUploadResponse:
        """Upload an image and record its metadata."""
        file_content = await file.read()
        file_ext = Path(file.filename).suffix.lstrip(".")

        file_url = await do_space.upload_file(
            file_content=file_content,
            file_ext=file_ext,
        )
        async with sessionmanager.session() as session:
            try:
                await self.crud.create(
                    session,
                    user_id=user_id,
                    file_path=file_url,
                    chapter=chapter,
                    ayat_start=ayat_start,
                    ayat_end=ayat_end,
                    script_id=script_id,
                )
                return ImageUploadResponse(
                    file_path=file_url,
                    message="Uploaded successfully",
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")

    async def get_user_uploads(self, user_id: int) -> list[ImageUploadRecord]:
        """Return all uploads for a specific user.

        The mobile client expects a successful request to return JSON even when
        no uploads exist.  Instead of raising ``HTTPException`` on an empty
        result set, simply return an empty list so the response body is ``[]``.
        """
        async with sessionmanager.session() as session:
            rows = await self.crud.get_by_user(session, user_id)

        if not rows:
            return []

        return [
            ImageUploadRecord(
                file_path=row.file_path,
                status=ProcessingStatus(row.status),
                chapter=row.chapter,
                ayat_start=row.ayat_start,
                ayat_end=row.ayat_end,
            )
            for row in rows
        ]


# Create a singleton instance
upload_service = UploadService()
