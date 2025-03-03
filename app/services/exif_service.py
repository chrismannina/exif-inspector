"""Service for EXIF data operations."""
import json
import subprocess
import os
import shutil
from pathlib import Path
from fastapi import HTTPException, UploadFile
import logging

from app.core.utils import (
    ensure_directory_exists, 
    validate_image_file, 
    validate_fuji_file, 
    validate_file_size,
    format_date_for_filename,
    sanitize_filename
)
from app.core.config import settings
from app.models.exif import FujiRecipeResponse, RecipeDetails

# Configure logging
logger = logging.getLogger(__name__)


class ExifService:
    """Service for handling EXIF operations."""
    
    @staticmethod
    def parse_exif_metadata(file_path):
        """
        Parse EXIF metadata from image file using exiftool.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            dict: Parsed EXIF metadata
            
        Raises:
            HTTPException: If there's an error processing the image
        """
        try:
            # Use subprocess to call exiftool and capture the output
            result = subprocess.run(
                ['exiftool', '-j', file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            
            # Parse the JSON output
            metadata_list = json.loads(result.stdout)
            metadata = metadata_list[0] if metadata_list else {}
            
            return metadata
        except subprocess.CalledProcessError as e:
            logger.error(f"Error processing image: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
        except json.JSONDecodeError:
            logger.error("Error parsing EXIF data")
            raise HTTPException(status_code=500, detail="Error parsing EXIF data")
    
    @staticmethod
    def parse_fuji_metadata(file_path):
        """
        Parse Fujifilm specific metadata from image file.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            dict: Parsed Fujifilm metadata
        """
        metadata = ExifService.parse_exif_metadata(file_path)
        
        # Extract Fujifilm recipe components
        film_simulation = metadata.get("FilmMode", metadata.get("FilmSimulation", "Unknown"))
        
        # Build comprehensive recipe information
        recipe_info = RecipeDetails(
            FilmSimulation=metadata.get("FilmMode", metadata.get("FilmSimulation", "Unknown")),
            DynamicRange=metadata.get("DynamicRange", "Unknown"),
            GrainEffect=metadata.get("GrainEffectRoughness", "Unknown"),
            ColorChrome=metadata.get("ColorChrome", "Unknown"),
            ColorChromeBlue=metadata.get("ColorChromeBlue", "Unknown"),
            WhiteBalance=metadata.get("WhiteBalance", "Unknown"),
            WBShift=metadata.get("WhiteBalanceFineTune", "Unknown"),
            Highlights=metadata.get("HighlightTone", "Unknown"),
            Shadows=metadata.get("ShadowTone", "Unknown"),
            Color=metadata.get("Saturation", "Unknown"),
            Sharpness=metadata.get("Sharpness", "Unknown"),
            NoiseReduction=metadata.get("NoiseReduction", "Unknown")
        )
        
        # Create a simplified recipe name from the film simulation
        recipe_name = film_simulation.split('/')[1] if '/' in film_simulation else film_simulation
        
        # Get values and ensure they're converted to strings
        aperture = metadata.get("Aperture", "Unknown")
        iso = metadata.get("ISO", "Unknown")
        focal_length = metadata.get("FocalLength", "Unknown")
        shutter_speed = metadata.get("ShutterSpeed", "Unknown")
        
        # Helper function to convert values to strings
        def to_str(value):
            return str(value) if value != "Unknown" else value
        
        response_data = FujiRecipeResponse(
            filename=os.path.basename(file_path),
            recipe=recipe_name,
            recipe_details=recipe_info,
            date=metadata.get("DateTimeOriginal", "Unknown Date"),
            camera_model=metadata.get("Model", "Unknown Camera"),
            lens_model=metadata.get("LensModel", "Unknown Lens"),
            aperture=to_str(aperture),
            shutter_speed=to_str(shutter_speed),
            iso=to_str(iso),
            focal_length=to_str(focal_length),
        )
        
        return response_data
    
    @staticmethod
    async def save_upload_file(file: UploadFile) -> Path:
        """
        Save an uploaded file to the temporary directory.
        
        Args:
            file: The uploaded file
            
        Returns:
            Path: Path to the saved file
            
        Raises:
            HTTPException: If there's an error saving the file
        """
        # Ensure the temporary directory exists
        temp_dir = ensure_directory_exists(settings.TEMP_DIR)
        
        # Create full path for the saved file
        file_path = temp_dir / file.filename
        
        try:
            # Save the uploaded file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
            return file_path
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    @staticmethod
    def cleanup_temp_files():
        """Clean up temporary files older than 1 hour."""
        # This is a placeholder for a more sophisticated cleanup mechanism
        # In a production environment, you might use a scheduled task
        # to clean up files based on age, etc.
        pass


# Create a singleton instance
exif_service = ExifService() 