#!/usr/bin/env python
"""
Custom Uvicorn server starter with enhanced configuration for large file uploads.
"""
import argparse
import os
import sys
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EXIF Checker API Server")
    parser.add_argument("--host", default=settings.HOST, help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=settings.PORT, help="Port to bind the server to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes (development only)")
    
    args = parser.parse_args()
    
    # Development mode
    print(f"Starting development server at {args.host}:{args.port}")
    
    # Configure Uvicorn with custom settings that allow for large file uploads
    # See: https://github.com/encode/uvicorn/blob/master/uvicorn/config.py
    config = uvicorn.Config(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers if args.workers > 1 else 1,
        # The following settings increase the allowed request body size
        http="httptools",  # Use httptools for better performance
        loop="uvloop",  # Use uvloop for better performance
        log_level="info"
    )
    
    # Set environment variable for BODY_SIZE_LIMIT
    os.environ["BODY_SIZE_LIMIT"] = str(int(settings.MAX_FILE_SIZE * 1024 * 1024))  # Convert MB to bytes
    
    server = uvicorn.Server(config)
    server.run() 