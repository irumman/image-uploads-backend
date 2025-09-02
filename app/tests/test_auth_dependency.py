import uuid
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.services.auth.auth_dependency import auth_dependency
from app.core.jwt_helper import jwt_helper
from app.db.crud.auth_sessions import AuthSessionCRUD


@pytest.mark.asyncio
async def test_auth_dependency_invalid_session(monkeypatch):
    token = jwt_helper.create_access_token(
        sub=f"1:{uuid.uuid4()}"
    )
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    async def fake_get_active_by_id(self, db, session_id):
        return None

    monkeypatch.setattr(AuthSessionCRUD, "get_active_by_id", fake_get_active_by_id)

    with pytest.raises(HTTPException) as exc:
        await auth_dependency(credentials, db=None)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_auth_dependency_valid_session(monkeypatch):
    session_uuid = uuid.uuid4()
    token = jwt_helper.create_access_token(
        sub=f"1:{session_uuid}"
    )
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    class Dummy:
        id = session_uuid

    async def fake_get_active_by_id(self, db, session_id):
        assert session_id == session_uuid
        return Dummy()

    monkeypatch.setattr(AuthSessionCRUD, "get_active_by_id", fake_get_active_by_id)

    auth = await auth_dependency(credentials, db=None)
    assert auth["user_id"] == 1
    assert auth["session_id"] == session_uuid

