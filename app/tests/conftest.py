import pytest
from fastapi import FastAPI
from app.api.v1.routes import router

@pytest.fixture
def app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/api")
    return app