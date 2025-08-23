from pydantic import BaseModel


class ImageUploadMetaData(BaseModel):
    """Metadata attached to an uploaded image."""

    chapter: int
    ayat_start: int
    ayat_end: int


class ImageUploadInputRequest(BaseModel):
    user_id: int
    meta_data: ImageUploadMetaData


class ImageUploadResponse(BaseModel):
    file_path: str
    message: str
