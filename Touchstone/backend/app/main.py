"""Touchstone — Open Source Marketing Attribution Engine.

Made with love by Mani Padisetti @ Almost Magic Tech Lab
MIT Licence
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.middleware.rate_limit import RateLimitMiddleware
from app.api.v1 import health, collect, identify, webhooks, campaigns, contacts


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Open Source Marketing Attribution — Almost Magic Tech Lab",
    lifespan=lifespan,
)

app.add_middleware(RateLimitMiddleware, max_requests=200, window_seconds=60)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Pixel runs on client websites — must accept any origin
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# API v1 routes
app.include_router(health.router, prefix="/api/v1")
app.include_router(collect.router, prefix="/api/v1")
app.include_router(identify.router, prefix="/api/v1")
app.include_router(webhooks.router, prefix="/api/v1")
app.include_router(campaigns.router, prefix="/api/v1")
app.include_router(contacts.router, prefix="/api/v1")

# Serve the tracking pixel
PIXEL_DIR = Path(__file__).parent.parent.parent / "pixel"


@app.get("/pixel/touchstone.js")
async def serve_pixel():
    pixel_path = PIXEL_DIR / "touchstone.js"
    return FileResponse(pixel_path, media_type="application/javascript")


@app.get("/pixel/test")
async def serve_test_page():
    test_path = PIXEL_DIR / "test.html"
    return FileResponse(test_path, media_type="text/html")


@app.get("/")
async def root():
    return {"message": "Touchstone — Open Source Marketing Attribution", "version": settings.app_version}
