"""Middleware for the application."""
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and response times."""
    
    async def dispatch(self, request: Request, call_next):
        """Process the request and log information."""
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log request details
        logger.info(
            f"{request.method} {request.url.path} "
            f"- Status: {response.status_code} "
            f"- Process time: {process_time:.4f}s"
        )
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers to responses."""
    
    async def dispatch(self, request: Request, call_next):
        """Process the request and add security headers."""
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        return response


class FileUploadSizeMiddleware(BaseHTTPMiddleware):
    """Middleware to handle file upload size at the Starlette level."""
    
    async def dispatch(self, request: Request, call_next):
        """Check if the request contains a file upload and handle size limits."""
        # Get the content length from the headers
        content_length = request.headers.get("content-length")
        
        # Always log max file size for debugging
        logger.info(f"MIDDLEWARE CHECK: MAX_FILE_SIZE is set to {settings.MAX_FILE_SIZE} MB")
        
        if content_length and request.headers.get("content-type", "").startswith("multipart/form-data"):
            # Convert to int
            content_length = int(content_length)
            
            # Calculate max size in bytes - HARDCODED to 50MB for testing
            max_size_mb = 50.0  # Force to 50MB
            max_size = int(max_size_mb * 1024 * 1024)  # Convert MB to bytes
            
            logger.info(f"Upload request detected: {content_length} bytes. Max allowed: {max_size} bytes ({max_size_mb} MB)")
            
            # Check if content length exceeds max size
            if content_length > max_size:
                logger.warning(f"Request size {content_length} bytes exceeds limit of {max_size} bytes")
                return JSONResponse(
                    status_code=413,
                    content={"detail": f"File size exceeds maximum allowed size of {max_size_mb} MB"}
                )
        
        # Continue with the request
        return await call_next(request)


def add_middleware(app: FastAPI):
    """Add all middleware to the application."""
    # Add file upload size middleware first (to catch large files before processing)
    app.add_middleware(FileUploadSizeMiddleware)
    
    # Add request logging middleware
    app.add_middleware(RequestLoggingMiddleware)
    
    # Add security headers middleware
    app.add_middleware(SecurityHeadersMiddleware) 