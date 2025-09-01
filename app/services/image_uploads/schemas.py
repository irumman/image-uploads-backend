from pydantic import BaseModel, field_serializer
from app.configs.constants import ProcessingStatus

class ImageUploadInputRequest(BaseModel):
    chapter: int
    line_start: int
    line_end: int
    script_id: int


class ImageUploadResponse(BaseModel):
    file_path: str
    message: str


class ImageUploadRecord(BaseModel):
    file_path: str
    status: ProcessingStatus
    chapter: int
    line_start: int
    line_end: int

    @field_serializer("status")
    def serialize_status(
        self, status: ProcessingStatus, _info
    ) -> str:
        return status.name.lower()
