"""Health check endpoints."""
from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.dependencies.exiftool import check_exiftool

# Create router
router = APIRouter(tags=["Health"])

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.get("/")
@limiter.limit("30/minute")
async def root(request: Request):
    """Root endpoint to verify API is running."""
    return {"message": "EXIF Checker API is running"}


@router.get("/health")
@limiter.limit("30/minute")
async def health_check(request: Request, _=Depends(check_exiftool)):
    """Health check endpoint to verify dependencies are installed."""
    return {"status": "healthy", "message": "EXIF Checker API is healthy"} 