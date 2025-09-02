import json
import io
import pytest
import uuid
from fastapi import FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient

from app.configs.constants import ProcessingStatus
from app.services.image_uploads.uploads import upload_service
from app.db.pg_engine import get_db_session
from app.core.jwt_helper import jwt_helper
from app.services.auth.auth_dependency import auth_dependency


@pytest.mark.asyncio
async def test_upload_success(monkeypatch, app: FastAPI):
    async def override_get_db_session():
        yield None
    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[auth_dependency] = lambda: {
        "user_id": 42,
        "session_id": uuid.uuid4(),
    }
    transport = ASGITransport(app=app)
    # 1) arrange: fake upload_service.upload_image to return a known response
    fake_resp = {"file_path": "https://example.com/foo.jpg", "message": "Uploaded successfully"}

    async def fake_upload_image(db, file, user_id, chapter, line_start, line_end, script_id):
        return fake_resp

    monkeypatch.setattr(upload_service, "upload_image", fake_upload_image)

    # 2) prepare form-data: a small in-memory file + metadata JSON
    file_bytes = b"JPEGDATA"
    metadata = {"chapter": 1, "line_start": 2, "line_end": 3, "script_id": 1}

    token = jwt_helper.create_access_token(
        sub=f"42:{uuid.uuid4()}"
    )
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/upload/",
            files={"file": ("test.jpg", io.BytesIO(file_bytes), "image/jpeg")},
            data={"metadata": json.dumps(metadata)},
            headers=headers,
        )

    # 3) assert
    assert response.status_code == 200
    assert response.json() == fake_resp
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_bad_metadata(app: FastAPI):
    async def override_get_db_session():
        yield None
    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[auth_dependency] = lambda: {
        "user_id": 1,
        "session_id": uuid.uuid4(),
    }
    transport = ASGITransport(app=app)
    # no monkeypatch: let model_validate_json blow up
    token = jwt_helper.create_access_token(
        sub=f"1:{uuid.uuid4()}"
    )
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/upload/",
            files={"file": ("test.jpg", io.BytesIO(b"x"), "image/jpeg")},
            data={"metadata": "not-a-json"},
            headers=headers,
        )
    # your code does `raise HTTPException()` on parse error,
    # so we expect a 400
    assert response.status_code == 400
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_service_failure(monkeypatch, app: FastAPI):
    async def override_get_db_session():
        yield None
    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[auth_dependency] = lambda: {
        "user_id": 1,
        "session_id": uuid.uuid4(),
    }
    transport = ASGITransport(app=app)
    # simulate service raising HTTPException
    async def broken_upload(*args, **kwargs):
        raise HTTPException(status_code=502, detail="upstream failed")

    monkeypatch.setattr(upload_service, "upload_image", broken_upload)

    metadata = {"chapter": 1, "line_start": 1, "line_end": 1, "script_id": 1}
    token = jwt_helper.create_access_token(
        sub=f"1:{uuid.uuid4()}"
    )
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/upload/",
            files={"file": ("foo.png", io.BytesIO(b"png"), "image/png")},
            data={"metadata": json.dumps(metadata)},
            headers=headers,
        )

    assert response.status_code == 502
    assert "upstream failed" in response.json().get("detail", "")
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_user_uploads(monkeypatch, app: FastAPI):
    async def override_get_db_session():
        yield None
    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[auth_dependency] = lambda: {
        "user_id": 42,
        "session_id": uuid.uuid4(),
    }
    transport = ASGITransport(app=app)
    fake_req = [
        {
            "file_path": "https://example.com/a.jpg",
            "status": ProcessingStatus.UPLOADED.value,
            "chapter": 1,
            "line_start": 1,
            "line_end": 2,
        },
        {
            "file_path": "https://example.com/b.jpg",
            "status": ProcessingStatus.PROCESSING.value,
            "chapter": 2,
            "line_start": 3,
            "line_end": 4,
        },
    ]

    fake_resp = [
        {
            "file_path": "https://example.com/a.jpg",
            "status": "uploaded",
            "chapter": 1,
            "line_start": 1,
            "line_end": 2,
        },
        {
            "file_path": "https://example.com/b.jpg",
            "status": "processing",
            "chapter": 2,
            "line_start": 3,
            "line_end": 4,
        },
    ]

    async def fake_get_user_uploads(db, user_id):
        return fake_req

    monkeypatch.setattr(upload_service, "get_user_uploads", fake_get_user_uploads)

    token = jwt_helper.create_access_token(
        sub=f"42:{uuid.uuid4()}"
    )
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/uploads/", headers=headers)

    assert resp.status_code == 200
    assert resp.json() == fake_resp
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_user_uploads_empty(monkeypatch, app: FastAPI):
    async def override_get_db_session():
        yield None
    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[auth_dependency] = lambda: {
        "user_id": 42,
        "session_id": uuid.uuid4(),
    }
    transport = ASGITransport(app=app)

    async def fake_get_user_uploads(db, user_id):
        return []

    monkeypatch.setattr(upload_service, "get_user_uploads", fake_get_user_uploads)

    token = jwt_helper.create_access_token(
        sub=f"42:{uuid.uuid4()}"
    )
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/uploads/", headers=headers)

    data = resp.json()
    assert resp.status_code == 200
    assert data == []
    assert isinstance(data, list)
    app.dependency_overrides.clear()



