"""API endpoints for EXIF data operations."""
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from fastapi import (
    APIRouter,
    File,
    UploadFile,
    Depends,
    Request,
    HTTPException,
    Form,
    status,
)
from fastapi.responses import JSONResponse, FileResponse
import shutil
import logging
from datetime import datetime

from app.dependencies.exiftool import check_exiftool
from app.models.exif import (
    ExifResponse,
    FujiRecipeResponse,
    BatchExifResponse,
    ErrorResponse,
)
from app.services.exif_service import exif_service
from app.core.utils import (
    validate_image_file,
    validate_fuji_file,
    format_date_for_filename,
    sanitize_filename,
)
from app.core.config import settings
from slowapi import Limiter
from slowapi.util import get_remote_address

# Configure logging
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(tags=["EXIF"])

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Constants
MAX_FILE_SIZE_MB = 50.0  # Hard-coded to 50MB


def validate_file_size(file: UploadFile, max_size_mb: float = MAX_FILE_SIZE_MB) -> None:
    """
    Validate that the uploaded file size does not exceed the maximum allowed size.

    Args:
        file: The uploaded file to validate
        max_size_mb: Maximum allowed file size in megabytes

    Raises:
        HTTPException: If the file size exceeds the maximum allowed size
    """
    # Get file size
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)  # Reset file position

    # Convert max size to bytes
    max_size_bytes = max_size_mb * 1024 * 1024

    # Log file size for debugging
    logger.debug(
        f"File size: {file_size} bytes, Max size: {max_size_bytes} bytes ({max_size_mb} MB)"
    )

    if file_size > max_size_bytes:
        logger.warning(
            f"File size {file_size} bytes exceeds limit of {max_size_bytes} bytes"
        )
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {max_size_mb} MB",
        )


@router.post("/analyze", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def analyze_exif(
    request: Request, file: UploadFile = File(...), _=Depends(check_exiftool)
):
    """
    Analyze EXIF data from an uploaded image file.

    Args:
        request: The request object
        file: The uploaded image file
        _: Dependency to check if ExifTool is available

    Returns:
        A dictionary containing the filename and extracted metadata

    Raises:
        HTTPException: If the file format is unsupported, the file size is too large,
                      or there's an error processing the file
    """
    # Check file extension
    if not validate_image_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file format"
        )

    # Validate file size
    validate_file_size(file, max_size_mb=MAX_FILE_SIZE_MB)

    # Save the uploaded file
    temp_file_path = await exif_service.save_upload_file(file)

    try:
        # Process the file with ExifTool
        metadata = exif_service.parse_exif_metadata(temp_file_path)

        # Return the metadata
        return {"filename": file.filename, "metadata": metadata}
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}",
        )
    finally:
        # Clean up the temporary file
        if temp_file_path.exists():
            temp_file_path.unlink()


@router.post("/fuji", response_model=FujiRecipeResponse, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def analyze_fuji_recipe(
    request: Request, file: UploadFile = File(...), _=Depends(check_exiftool)
):
    """
    Extract Fujifilm recipe data from a Fujifilm image.

    Args:
        request: The request object
        file: The uploaded Fujifilm image file
        _: Dependency to check if ExifTool is available

    Returns:
        A FujiRecipeResponse object containing the recipe details

    Raises:
        HTTPException: If the file format is unsupported, the file size is too large,
                      or there's an error processing the file
    """
    # Check file extension
    if not validate_fuji_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Only Fujifilm images (JPG, RAF) are supported.",
        )

    # Validate file size
    validate_file_size(file, max_size_mb=MAX_FILE_SIZE_MB)

    # Save the uploaded file
    temp_file_path = await exif_service.save_upload_file(file)

    try:
        # Process the file to extract Fujifilm recipe
        response_data = exif_service.parse_fuji_metadata(temp_file_path)

        return response_data
    except Exception as e:
        logger.error(f"Error processing Fujifilm image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing Fujifilm image: {str(e)}",
        )
    finally:
        # Clean up the temporary file
        if temp_file_path.exists():
            temp_file_path.unlink()


@router.post(
    "/batch", response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK
)
@limiter.limit("5/minute")
async def analyze_batch(
    request: Request, files: List[UploadFile] = File(...), _=Depends(check_exiftool)
):
    """
    Batch process multiple images for EXIF data.

    Args:
        request: The request object
        files: List of uploaded image files
        _: Dependency to check if ExifTool is available

    Returns:
        A list of dictionaries containing the filename and extracted metadata for each file

    Raises:
        HTTPException: If no files are provided
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No files provided"
        )

    # Prepare result containers
    results = []
    errors = []

    for file in files:
        # Check file extension
        if not validate_image_file(file.filename):
            errors.append(
                {"filename": file.filename, "error": "Unsupported file format"}
            )
            continue

        try:
            # Validate file size
            validate_file_size(file, max_size_mb=MAX_FILE_SIZE_MB)

            # Save the uploaded file
            temp_file_path = await exif_service.save_upload_file(file)

            try:
                # Process the file with ExifTool
                metadata = exif_service.parse_exif_metadata(temp_file_path)

                # Add to successful results
                results.append({"filename": file.filename, "metadata": metadata})
            except Exception as e:
                logger.error(f"Error processing file {file.filename}: {str(e)}")
                # Add to errors
                errors.append({"filename": file.filename, "error": str(e)})
            finally:
                # Clean up the temporary file
                if temp_file_path.exists():
                    temp_file_path.unlink()
        except HTTPException as e:
            # Add to errors
            errors.append({"filename": file.filename, "error": e.detail})

    # Include errors in the response if there are any
    if errors:
        logger.warning(f"Batch processing completed with {len(errors)} errors")

    # Return results
    return results


@router.post("/rename", response_model=Dict[str, str], status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def rename_proposal(
    request: Request, file: UploadFile = File(...), _=Depends(check_exiftool)
):
    """
    Generate a filename proposal based on EXIF data.

    Args:
        request: The request object
        file: The uploaded image file
        _: Dependency to check if ExifTool is available

    Returns:
        A dictionary containing the original filename and the proposed new filename

    Raises:
        HTTPException: If the file format is unsupported, the file size is too large,
                      or there's an error processing the file
    """
    # Check file extension
    if not validate_image_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file format"
        )

    # Validate file size
    validate_file_size(file, max_size_mb=50.0)

    # Save the uploaded file
    temp_file_path = await exif_service.save_upload_file(file)

    try:
        # Process the file with ExifTool
        metadata = exif_service.parse_exif_metadata(temp_file_path)

        # Generate filename components
        filename, ext = os.path.splitext(file.filename)
        date_str = metadata.get("DateTimeOriginal", "")
        camera = metadata.get("Model", "").replace(" ", "_")
        lens = metadata.get("LensModel", "").replace(" ", "_")

        # Get aperture, shutter speed, and ISO if available
        aperture = metadata.get("Aperture", "")
        aperture_str = f"f{aperture}" if aperture else ""

        shutter = metadata.get("ShutterSpeed", "")
        shutter_str = f"{shutter}s" if shutter else ""

        iso = metadata.get("ISO", "")
        iso_str = f"ISO{iso}" if iso else ""

        # Format date
        date_formatted = format_date_for_filename(date_str)

        # Construct filename
        elements = [date_formatted, camera, lens, aperture_str, shutter_str, iso_str]
        new_filename = "_".join([e for e in elements if e])

        # Sanitize and add extension
        new_filename = sanitize_filename(new_filename) + ext

        # Return result
        return {
            "original_filename": file.filename,
            "proposed_filename": new_filename,
            "metadata_used": {
                "date": date_str,
                "camera": camera,
                "lens": lens,
                "aperture": aperture,
                "shutter_speed": shutter,
                "iso": iso,
            },
        }
    except Exception as e:
        logger.error(f"Error processing file for rename: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    finally:
        # Clean up the temporary file
        if temp_file_path.exists():
            temp_file_path.unlink()
