import pytest
from app.services.image_uploads.uploads import UploadService
from app.configs.constants import ProcessingStatus


class DummyRow:
    def __init__(self, file_path: str, status: ProcessingStatus, chapter: int, line_start: int, line_end: int):
        self.file_path = file_path
        self.status = status
        self.chapter = chapter
        self.line_start = line_start
        self.line_end = line_end


@pytest.mark.asyncio
async def test_get_user_uploads_serializes_status(monkeypatch):
    service = UploadService()

    async def fake_get_by_user(db, user_id):
        return [
            DummyRow("https://a.jpg", ProcessingStatus.UPLOADED, 1, 1, 2),
            DummyRow("https://b.jpg", ProcessingStatus.PROCESSING, 2, 3, 4),
        ]

    monkeypatch.setattr(service.crud, "get_by_user", fake_get_by_user)

    records = await service.get_user_uploads(None, 5)
    assert records[0].model_dump() == {
        "file_path": "https://a.jpg",
        "status": "uploaded",
        "chapter": 1,
        "line_start": 1,
        "line_end": 2,
    }
    assert records[1].model_dump()["status"] == "processing"


@pytest.mark.asyncio
async def test_get_user_uploads_empty(monkeypatch):
    service = UploadService()

    async def fake_get_by_user(db, user_id):
        return []

    monkeypatch.setattr(service.crud, "get_by_user", fake_get_by_user)

    records = await service.get_user_uploads(None, 5)
    assert records == []
    assert isinstance(records, list)
