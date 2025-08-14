from fastapi import FastAPI
from app.api.v1.routes import router
from app.configs.settings import settings

app = FastAPI(
    title="Image Uploads Backend",
    description="API for image uploads",
    version="0.0.1",
    debug=settings.debug
)

app.include_router(router, prefix="/api")
