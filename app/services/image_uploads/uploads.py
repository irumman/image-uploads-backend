from pathlib import Path

from datetime import datetime, timezone
from fastapi import UploadFile, HTTPException
from app.db.pg_dml import insert_record
from app.db.pg_engine import sessionmanager
from app.db.models.image_uploads import ImageUploads
from app.services.image_uploads.schemas import ImageUploadResponse
from app.configs.constants import ProcessingStatus
from app.services.storage.do_space import do_space

class UploadService:
    def __init__(self):
        pass

    async def upload_image(self, file: UploadFile, user_id: int,
                      chapter: int, ayat_start: int, ayat_end: int) -> ImageUploadResponse:
        """
        Upload an image and insert record into PostgreSQL database.
        
        Args:
            file (UploadFile): The uploaded image file
            user_id (int): The ID of the user uploading the image
            chapter (int): The chapter number
            ayat_start (int): The starting ayat number
            ayat_end (int): The ending ayat number
        
        Returns:
            ImageUploadResponse: The response containing file_path and success message
        
        Raises:
            HTTPException: If upload fails or validation fails
        """
        file_content = await file.read()
        file_ext = Path(file.filename).suffix.lstrip(".")

        file_url = await do_space.upload_file(
            file_content=file_content,
            file_ext=file_ext
        )
        async with sessionmanager.session() as session:
            try:
                upload_record = ImageUploads(
                    file_path=file_url,
                    user_id=user_id,
                    chapter=chapter,
                    ayat_start=ayat_start,
                    ayat_end=ayat_end,
                    status=ProcessingStatus.UPLOADED,
                    upload_timestamp=datetime.now(timezone.utc)

                )
                await insert_record(session, upload_record)

                return ImageUploadResponse(
                    file_path=file_url,
                    message="Uploaded successfully"
                )
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")

# Create a singleton instance
upload_service = UploadService()