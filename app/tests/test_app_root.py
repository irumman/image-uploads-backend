import pytest
from httpx import AsyncClient, ASGITransport

@pytest.mark.asyncio
async def test_root(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/")
    assert r.status_code == 200
    assert r.json() == {"message": "Hello World"}