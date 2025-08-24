from pydantic import BaseModel

class ImageUploadInputRequest(BaseModel):
    user_id: int
    script_id: int
    chapter: int
    ayat_start: int
    ayat_end: int


class ImageUploadResponse(BaseModel):
    file_path: str
    message: str


class UserImage(BaseModel):
    file_path: str
    script_id: int
    chapter: int
    ayat_start: int
    ayat_end: int
