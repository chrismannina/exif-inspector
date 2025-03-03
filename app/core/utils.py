"""Utility functions for the application."""
import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from fastapi import HTTPException


def ensure_directory_exists(directory_path):
    """Ensure a directory exists, creating it if necessary"""
    path = Path(directory_path)
    path.mkdir(exist_ok=True, parents=True)
    return path


def format_date_for_filename(date_str):
    """Format a date string for use in filenames"""
    try:
        # Try to parse the date string
        if not date_str or date_str == "Unknown Date":
            return datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Replace colons and spaces for filename safety
        return date_str.replace(":", "").replace(" ", "_")
    except Exception:
        # Fall back to current date/time if parsing fails
        return datetime.now().strftime("%Y%m%d_%H%M%S")


def sanitize_filename(filename):
    """Sanitize a filename to ensure it's safe for all operating systems"""
    # Replace problematic characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length (adjust if needed)
    if len(filename) > 255:
        base, ext = os.path.splitext(filename)
        filename = base[:255-len(ext)] + ext
    
    return filename


def check_exiftool_available():
    """Check if ExifTool is available in the system"""
    try:
        result = subprocess.run(
            ['exiftool', '-ver'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def validate_image_file(filename):
    """Validate if a file is an acceptable image format"""
    allowed_extensions = ('.jpg', '.jpeg', '.png', '.raf', '.tiff', '.tif')
    return filename.lower().endswith(allowed_extensions)


def validate_fuji_file(filename):
    """Validate if a file is a Fujifilm compatible format"""
    allowed_extensions = ('.jpg', '.jpeg', '.raf')
    return filename.lower().endswith(allowed_extensions)


def validate_file_size(file, max_size_mb=None):
    """
    Validate if a file is below the maximum allowed size
    
    Args:
        file: UploadFile object
        max_size_mb: Maximum allowed size in MB (default: from environment or 10MB)
        
    Returns:
        bool: True if file size is valid, False otherwise
    
    Raises:
        HTTPException: If file size exceeds the maximum allowed size
    """
    if max_size_mb is None:
        # Get maximum file size from environment, default to 10MB
        max_size_mb = float(os.getenv("MAX_FILE_SIZE", "10"))
    
    # Get file size in bytes
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)  # Reset file pointer for subsequent operations
    
    # Convert MB to bytes
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds maximum allowed size of {max_size_mb} MB"
        )
    
    return True 