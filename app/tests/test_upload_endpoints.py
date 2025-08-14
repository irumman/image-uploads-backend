import json
import pytest
import io
from fastapi import FastAPI, HTTPException
from httpx import AsyncClient, ASGITransport
from app.api.v1.routes import router
from app.services.image_uploads.uploads import upload_service


@pytest.mark.asyncio
async def test_upload_success(monkeypatch, app: FastAPI):
    transport = ASGITransport(app=app)
    # 1) arrange: fake upload_service.upload_image to return a known response
    fake_resp = {"file_path": "https://example.com/foo.jpg", "message": "Uploaded successfully"}
    async def fake_upload_image(file, user_id, chapter, ayat_start, ayat_end):
        return fake_resp
    monkeypatch.setattr(upload_service, "upload_image", fake_upload_image)

    # 2) prepare form-data: a small in-memory file + metadata JSON
    file_bytes = b"JPEGDATA"
    metadata = {"user_id": 42, "chapter": 1, "ayat_start": 2, "ayat_end": 3}

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/upload/",
            files={"file": ("test.jpg", io.BytesIO(file_bytes), "image/jpeg")},
            data={"metadata": json.dumps(metadata)}
        )

    # 3) assert
    assert response.status_code == 200
    assert response.json() == fake_resp

@pytest.mark.asyncio
async def test_upload_bad_metadata(app: FastAPI):
    transport = ASGITransport(app=app)
    # no monkeypatch: let model_validate_json blow up
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/upload/",
            files={"file": ("test.jpg", io.BytesIO(b"x"), "image/jpeg")},
            data={"metadata": "not-a-json"}
        )
    # your code does `raise HTTPException()` on parse error,
    # so we expect a 500 (or whatever default you get)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_upload_service_failure(monkeypatch, app: FastAPI):
    transport = ASGITransport(app=app)
    # simulate service raising HTTPException
    async def broken_upload(*args, **kwargs):
        raise HTTPException(status_code=502, detail="upstream failed")
    monkeypatch.setattr(upload_service, "upload_image", broken_upload)

    metadata = {"user_id": 1, "chapter": 1, "ayat_start": 1, "ayat_end": 1}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/upload/",
            files={"file": ("foo.png", io.BytesIO(b"png"), "image/png")},
            data={"metadata": json.dumps(metadata)}
        )

    assert response.status_code == 502
    assert "upstream failed" in response.json().get("detail", "")