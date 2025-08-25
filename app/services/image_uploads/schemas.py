from pydantic import BaseModel, field_serializer
from app.configs.constants import ProcessingStatus

class ImageUploadInputRequest(BaseModel):
    user_id: int
    chapter: int
    ayat_start: int
    ayat_end: int
    script_id: int


class ImageUploadResponse(BaseModel):
    file_path: str
    message: str


class ImageUploadRecord(BaseModel):
    file_path: str
    status: ProcessingStatus
    chapter: int
    ayat_start: int
    ayat_end: int

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, value: str | int | ProcessingStatus):
        """Allow case-insensitive string or integer inputs for ``status``.

        The response model is declared with :class:`ProcessingStatus`, which
        means FastAPI will validate any data returned from the service.  During
        testing the service is often monkeypatched to return dictionaries with
        lowercase string statuses (e.g. ``"uploaded"``).  Without this
        validator such values fail enum validation, leading to
        ``ResponseValidationError``.  Converting them here keeps the public API
        stable while permitting more flexible internal representations.
        """
        if isinstance(value, str):
            return ProcessingStatus[value.upper()]
        return value

    @field_serializer("status")
    def serialize_status(
        self, status: ProcessingStatus, _info
    ) -> str:
        return status.name.lower()
