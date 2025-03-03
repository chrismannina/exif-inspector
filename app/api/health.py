"""Health check endpoints."""
from typing import Dict, Any
from fastapi import APIRouter, Depends, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.dependencies.exiftool import check_exiftool
from app.core.config import settings

# Create router
router = APIRouter(tags=["Health"])

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.get("/", response_model=Dict[str, str], status_code=status.HTTP_200_OK)
@limiter.limit("30/minute")
async def root(request: Request) -> Dict[str, str]:
    """
    Root endpoint to verify API is running.
    
    Args:
        request: The request object for rate limiting
        
    Returns:
        A dictionary with a status message
    """
    return {"message": "EXIF Checker API is running"}


@router.get("/health", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
@limiter.limit("30/minute")
async def health_check(request: Request, _=Depends(check_exiftool)) -> Dict[str, Any]:
    """
    Health check endpoint to verify dependencies are installed.
    
    Args:
        request: The request object for rate limiting
        _: Dependency to check if ExifTool is available
        
    Returns:
        A dictionary with health status, message, and configuration details
    """
    return {
        "status": "healthy", 
        "message": "EXIF Checker API is healthy",
        "config": {
            "max_file_size": settings.MAX_FILE_SIZE,
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT
        }
    } 