import pytest
from fastapi import FastAPI, HTTPException
from httpx import AsyncClient, ASGITransport

from app.services.image_uploads.uploads import upload_service


@pytest.mark.asyncio
async def test_get_script_images_success(monkeypatch, app: FastAPI):
    transport = ASGITransport(app=app)

    fake_images = [
        {"file_path": "https://example.com/a.jpg", "script_id": 42, "chapter": 1, "ayat_start": 1, "ayat_end": 2},
        {"file_path": "https://example.com/b.jpg", "script_id": 42, "chapter": 2, "ayat_start": 3, "ayat_end": 4},
    ]

    async def fake_get_script_images(script_id: int):
        return fake_images

    monkeypatch.setattr(upload_service, "get_script_images", fake_get_script_images)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/images/42/")

    assert resp.status_code == 200
    assert resp.json() == fake_images


@pytest.mark.asyncio
async def test_get_script_images_failure(monkeypatch, app: FastAPI):
    transport = ASGITransport(app=app)

    async def broken_get_script_images(script_id: int):
        raise HTTPException(status_code=404, detail="not found")

    monkeypatch.setattr(upload_service, "get_script_images", broken_get_script_images)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/images/42/")

    assert resp.status_code == 404
    assert resp.json()["detail"] == "not found"
