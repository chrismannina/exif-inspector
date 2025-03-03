"""Middleware for the application."""
import time
import logging
from typing import Callable, Awaitable
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
from app.core.config import settings

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and response times."""
    
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """
        Process the request and log information.
        
        Args:
            request: The incoming request
            call_next: The next middleware or route handler
            
        Returns:
            The response from the next middleware or route handler
        """
        start_time = time.time()
        
        try:
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
        except Exception as e:
            # Log the error
            process_time = time.time() - start_time
            logger.error(
                f"{request.method} {request.url.path} "
                f"- Error: {str(e)} "
                f"- Process time: {process_time:.4f}s"
            )
            # Re-raise the exception for the global exception handler
            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers to responses."""
    
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """
        Process the request and add security headers.
        
        Args:
            request: The incoming request
            call_next: The next middleware or route handler
            
        Returns:
            The response with added security headers
        """
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response


class FileUploadSizeMiddleware(BaseHTTPMiddleware):
    """Middleware to handle file upload size at the Starlette level."""
    
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """
        Check if the request contains a file upload and handle size limits.
        
        Args:
            request: The incoming request
            call_next: The next middleware or route handler
            
        Returns:
            The response or a 413 error if the file is too large
        """
        # Get the content length from the headers
        content_length = request.headers.get("content-length")
        
        # Always log max file size for debugging
        logger.debug(f"MAX_FILE_SIZE is set to {settings.MAX_FILE_SIZE} MB")
        
        if content_length and request.headers.get("content-type", "").startswith("multipart/form-data"):
            try:
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
            except ValueError:
                logger.warning(f"Invalid content length header: {content_length}")
        
        # Continue with the request
        return await call_next(request)


def add_middleware(app: FastAPI) -> None:
    """
    Add all middleware to the application.
    
    Args:
        app: The FastAPI application
    """
    # Add file upload size middleware first (to catch large files before processing)
    app.add_middleware(FileUploadSizeMiddleware)
    
    # Add request logging middleware
    app.add_middleware(RequestLoggingMiddleware)
    
    # Add security headers middleware
    app.add_middleware(SecurityHeadersMiddleware) 