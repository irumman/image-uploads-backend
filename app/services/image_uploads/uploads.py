from pathlib import Path
from datetime import datetime, timezone
from fastapi import UploadFile, HTTPException

from app.db.pg_dml import insert_record
from app.db.pg_engine import sessionmanager
from app.db.models.image_uploads import ImageUploads
from app.services.image_uploads.schemas import ImageUploadResponse
from app.services.storage.do_space import do_space


class UploadService:
    def __init__(self) -> None:
        pass

    async def upload_image(self, file: UploadFile, user_id: int, meta_data: dict) -> ImageUploadResponse:
        """Upload an image and store metadata in the database."""
        file_content = await file.read()
        file_ext = Path(file.filename).suffix.lstrip(".")

        file_url = await do_space.upload_file(
            file_content=file_content,
            file_ext=file_ext,
        )
        async with sessionmanager.session() as session:
            try:
                upload_record = ImageUploads(
                    file_path=file_url,
                    user_id=user_id,
                    meta_data=meta_data,
                    upload_timestamp=datetime.now(timezone.utc),
                )
                await insert_record(session, upload_record)

                return ImageUploadResponse(
                    file_path=file_url,
                    message="Uploaded successfully",
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")


# Create a singleton instance
upload_service = UploadService()
