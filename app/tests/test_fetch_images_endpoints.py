import pytest
from fastapi import FastAPI, HTTPException
from httpx import AsyncClient, ASGITransport

from app.services.image_uploads.uploads import upload_service
from app.db.crud.image_uploads import ImageUploadCrud


@pytest.mark.asyncio
async def test_get_user_images_success(monkeypatch, app: FastAPI):
    transport = ASGITransport(app=app)

    fake_images = [
        {"file_path": "https://example.com/a.jpg", "script_id": 7, "chapter": 1, "ayat_start": 1, "ayat_end": 2},
        {"file_path": "https://example.com/b.jpg", "script_id": 8, "chapter": 2, "ayat_start": 3, "ayat_end": 4},
    ]

    async def fake_get_user_images(user_id: int):
        return fake_images

    monkeypatch.setattr(upload_service, "get_user_images", fake_get_user_images)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/images/123/")

    assert resp.status_code == 200
    assert resp.json() == fake_images


@pytest.mark.asyncio
async def test_get_user_images_not_found(monkeypatch, app: FastAPI):
    transport = ASGITransport(app=app)

    async def fake_get_by_user(self, user_id: int):
        return []

    monkeypatch.setattr(ImageUploadCrud, "get_by_user", fake_get_by_user)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/images/123/")

    assert resp.status_code == 404
    assert resp.json()["detail"] == "Images not found"
