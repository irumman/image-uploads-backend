from pydantic import BaseModel

class ImageUploadInputRequest(BaseModel):
    user_id: int
    chapter: int
    ayat_start: int
    ayat_end: int
    script_id: int


class ImageUploadResponse(BaseModel):
    file_path: str
    message: str
