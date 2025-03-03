"""Middleware for the application."""
import time
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging

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


def add_middleware(app: FastAPI):
    """Add all middleware to the application."""
    # Add request logging middleware
    app.add_middleware(RequestLoggingMiddleware)
    
    # Add security headers middleware
    app.add_middleware(SecurityHeadersMiddleware) 