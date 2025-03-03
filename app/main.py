"""Main FastAPI application."""
import logging
from pathlib import Path
import os

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.models.exif import ErrorResponse
from app.api.v1.router import api_router
from app.api.health import router as health_router
from app.core.utils import ensure_directory_exists
from app.core.middleware import add_middleware

# Configure logging
logging.basicConfig(
    level=settings.get_log_level(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=lambda x: x.client.host)

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url=None,  # We'll serve these manually for custom paths/styling
    redoc_url=None,
)

# Add static files
app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")

# Root route
@app.get("/", include_in_schema=False)
async def root():
    """Redirect to UI."""
    return RedirectResponse(url="/ui")

# UI route
@app.get("/ui", response_class=HTMLResponse, include_in_schema=False)
async def ui():
    """Serve the UI frontend."""
    try:
        with open("frontend/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="UI not found")

# Add custom OpenAPI endpoints
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI documentation."""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{settings.PROJECT_NAME} - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """ReDoc documentation."""
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{settings.PROJECT_NAME} - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    )

# Custom OpenAPI schema
def custom_openapi():
    """Generate custom OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.PROJECT_DESCRIPTION,
        routes=app.routes,
    )
    
    # Add custom OpenAPI tags
    openapi_schema["tags"] = [
        {"name": "Health", "description": "Health check endpoints"},
        {"name": "EXIF", "description": "EXIF data extraction endpoints"},
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Add rate limiter to application
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
add_middleware(app)

# Include routers
app.include_router(health_router)
app.include_router(api_router, prefix=settings.API_V1_STR)

# Create a temporary directory for uploaded files
ensure_directory_exists(settings.TEMP_DIR)


# Handle HTTP exceptions
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom handler for HTTP exceptions to standardize error responses.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(detail=str(exc.detail)).dict()
    )


# Handle general exceptions
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Custom handler for general exceptions to standardize error responses.
    """
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(detail="An unexpected error occurred").dict()
    )


# Clean up on shutdown
@app.on_event("shutdown")
def cleanup():
    """
    Clean up resources when shutting down.
    """
    logger.info("Cleaning up resources")
    try:
        # Delete all files in the temp directory
        for item in settings.TEMP_DIR.glob("*"):
            if item.is_file():
                item.unlink()
        logger.info("Temporary files cleaned up")
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Initialize resources on startup.
    """
    logger.info("Starting EXIF Checker API")
    
    # Ensure temp directory exists
    ensure_directory_exists(settings.TEMP_DIR)
    logger.info(f"Temporary directory set up at {settings.TEMP_DIR}") 