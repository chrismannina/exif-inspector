#!/usr/bin/env python
"""
EXIF Checker API Server Runner

This script starts the EXIF Checker API server using Uvicorn for development
or prepares it for Gunicorn in production.
"""
import uvicorn
import argparse
import os
import sys
from typing import Optional
from app.core.config import settings


def run_server(
    host: str = settings.HOST,
    port: int = settings.PORT,
    reload: bool = False,
    workers: int = 1,
    log_level: str = "info",
    production: bool = False,
) -> None:
    """
    Run the EXIF Checker API server.

    Args:
        host: Host to bind the server to
        port: Port to bind the server to
        reload: Enable auto-reload for development
        workers: Number of worker processes
        log_level: Logging level (debug, info, warning, error, critical)
        production: Use production settings
    """
    if production:
        print("For production deployment, use gunicorn:")
        print(
            f"gunicorn app.main:app --workers {workers} --worker-class uvicorn.workers.UvicornWorker --bind {host}:{port}"
        )
        sys.exit(0)

    # Development mode
    print(f"Starting development server at {host}:{port}")

    try:
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=reload,
            workers=workers if workers > 1 else 1,
            log_level=log_level,
        )
    except Exception as e:
        print(f"Error starting server: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EXIF Checker API Server")
    parser.add_argument(
        "--host", default=settings.HOST, help="Host to bind the server to"
    )
    parser.add_argument(
        "--port", type=int, default=settings.PORT, help="Port to bind the server to"
    )
    parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (development only)",
    )
    parser.add_argument(
        "--log-level",
        choices=["debug", "info", "warning", "error", "critical"],
        default="info",
        help="Logging level",
    )
    parser.add_argument("--prod", action="store_true", help="Use production settings")

    args = parser.parse_args()

    run_server(
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers,
        log_level=args.log_level,
        production=args.prod,
    )
