import pytest
import uuid
from fastapi import FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient

from app.services.auth.email_password.login_user_pass import LoginUserPass
from app.services.auth.email_password.logout import Logout
from app.services.auth.email_password.schemas import (
    EmailRegistrationResponse,
    LoginEmailResponse,
    LogoutResponse,
)
from app.services.auth.email_password.email_registration import email_registration
from app.db.pg_engine import get_db_session
from app.core.jwt_helper import jwt_helper
from app.services.auth.auth_dependency import auth_dependency


@pytest.mark.asyncio
async def test_register_success(monkeypatch, app: FastAPI):
    async def override_get_db_session():
        yield None
    app.dependency_overrides[get_db_session] = override_get_db_session

    async def fake_register(db, user_data):
        return EmailRegistrationResponse(
            name=user_data.name,
            email=user_data.email,
            message="User registered successfully.",
        )

    monkeypatch.setattr(email_registration, "register", fake_register)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/register",
            json={
                "name": "Test User",
                "email": "user@example.com",
                "password": "secret",
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "name": "Test User",
        "email": "user@example.com",
        "message": "User registered successfully.",
    }
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_login_success(monkeypatch, app: FastAPI):
    async def override_get_db_session():
        yield None
    app.dependency_overrides[get_db_session] = override_get_db_session

    async def fake_login(self, request):
        return LoginEmailResponse(
            user={"id": 1, "name": "Test User", "email": "user@example.com"},
            access_token="token123",
            refresh_token="refresh123",
            message="Login successful",
        )

    monkeypatch.setattr(LoginUserPass, "login_with_password", fake_login)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/login",
            json={"email": "user@example.com", "password": "secret"},
        )

    assert response.status_code == 200
    assert response.json() == {
        "user": {
            "id": 1,
            "name": "Test User",
            "email": "user@example.com",
        },
        "access_token": "token123",
        "token_type": "Bearer",
        "refresh_token": "refresh123",
        "message": "Login successful",
    }
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_login_invalid_credentials(monkeypatch, app: FastAPI):
    async def override_get_db_session():
        yield None
    app.dependency_overrides[get_db_session] = override_get_db_session

    async def fake_login(self, request):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    monkeypatch.setattr(LoginUserPass, "login_with_password", fake_login)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/login",
            json={"email": "user@example.com", "password": "bad"},
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_logout_success(monkeypatch, app: FastAPI):
    async def override_get_db_session():
        yield None
    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[auth_dependency] = lambda: {
        "user_id": 1,
        "session_id": uuid.uuid4(),
    }

    async def fake_logout(self):
        return LogoutResponse(message="Logout successful")

    monkeypatch.setattr(Logout, "logout", fake_logout)
    transport = ASGITransport(app=app)
    token = jwt_helper.create_access_token(
        sub=f"1:{uuid.uuid4()}"
    )
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/logout",
            json={"refresh_token": "token"},
            headers=headers,
        )

    assert response.status_code == 200
    assert response.json() == {"message": "Logout successful"}
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_logout_invalid_session(monkeypatch, app: FastAPI):
    async def override_get_db_session():
        yield None
    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[auth_dependency] = lambda: {
        "user_id": 1,
        "session_id": uuid.uuid4(),
    }

    async def fake_logout(self):
        raise HTTPException(status_code=401, detail="Invalid session")

    monkeypatch.setattr(Logout, "logout", fake_logout)
    transport = ASGITransport(app=app)
    token = jwt_helper.create_access_token(
        sub=f"1:{uuid.uuid4()}"
    )
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/logout",
            json={"refresh_token": "bad"},
            headers=headers,
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid session"
    app.dependency_overrides.clear()
