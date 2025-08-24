import pytest
from app.services.image_uploads.uploads import UploadService
from app.configs.constants import ProcessingStatus
import app.services.image_uploads.uploads as uploads_module


class DummyRow:
    def __init__(self, file_path: str, status: ProcessingStatus, chapter: int, ayat_start: int, ayat_end: int):
        self.file_path = file_path
        self.status = status
        self.chapter = chapter
        self.ayat_start = ayat_start
        self.ayat_end = ayat_end


class DummySessionContext:
    async def __aenter__(self):
        return object()

    async def __aexit__(self, exc_type, exc, tb):
        pass


class DummySessionManager:
    def session(self):
        return DummySessionContext()


@pytest.mark.asyncio
async def test_get_user_uploads_serializes_status(monkeypatch):
    service = UploadService()

    async def fake_get_by_user(session, user_id):
        return [
            DummyRow("https://a.jpg", ProcessingStatus.UPLOADED, 1, 1, 2),
            DummyRow("https://b.jpg", ProcessingStatus.PROCESSING, 2, 3, 4),
        ]

    monkeypatch.setattr(service.crud, "get_by_user", fake_get_by_user)
    monkeypatch.setattr(uploads_module, "sessionmanager", DummySessionManager())

    records = await service.get_user_uploads(5)
    assert records[0].model_dump() == {
        "file_path": "https://a.jpg",
        "status": "uploaded",
        "chapter": 1,
        "ayat_start": 1,
        "ayat_end": 2,
    }
    assert records[1].model_dump()["status"] == "processing"


@pytest.mark.asyncio
async def test_get_user_uploads_empty(monkeypatch):
    service = UploadService()

    async def fake_get_by_user(session, user_id):
        return []

    monkeypatch.setattr(service.crud, "get_by_user", fake_get_by_user)
    monkeypatch.setattr(uploads_module, "sessionmanager", DummySessionManager())

    records = await service.get_user_uploads(5)
    assert records == []
