"""Dependencies for ExifTool functionality."""
from fastapi import HTTPException, Depends

from app.core.utils import check_exiftool_available


async def check_exiftool():
    """
    Dependency to check if ExifTool is available.

    Raises:
        HTTPException: If ExifTool is not installed or not in PATH.
    """
    if not check_exiftool_available():
        raise HTTPException(
            status_code=500,
            detail="ExifTool is not installed or not available in PATH. Please install ExifTool to use this API.",
        )
    return True
