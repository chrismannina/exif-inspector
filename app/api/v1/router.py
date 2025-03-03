"""Main API router for v1 endpoints."""
from fastapi import APIRouter

from app.api.v1.endpoints import router as exif_router

# Create API v1 router
api_router = APIRouter()

# Include the EXIF router
api_router.include_router(exif_router, prefix="/exif")
