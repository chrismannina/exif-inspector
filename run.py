#!/usr/bin/env python
"""
EXIF Checker API Server Runner

This script starts the EXIF Checker API server using uvicorn for development
or prepares it for Gunicorn in production.
"""
import uvicorn
import argparse
import os
import sys
from app.core.config import settings

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EXIF Checker API Server")
    parser.add_argument("--host", default=settings.HOST, help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=settings.PORT, help="Port to bind the server to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes (development only)")
    parser.add_argument("--prod", action="store_true", help="Use production settings")
    
    args = parser.parse_args()
    
    # In production mode, print a message and exit - use gunicorn
    if args.prod:
        print("For production deployment, use gunicorn:")
        print("gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000")
        sys.exit(0)
    
    # Development mode
    print(f"Starting development server at {args.host}:{args.port}")
    uvicorn.run(
        "app.main:app", 
        host=args.host, 
        port=args.port,
        reload=args.reload,
        workers=args.workers if args.workers > 1 else 1
    ) 