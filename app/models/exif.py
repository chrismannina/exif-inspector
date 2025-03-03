"""EXIF data models."""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional


class ExifResponse(BaseModel):
    """Model for EXIF data response"""

    filename: str
    metadata: Dict[str, Any]


class RecipeDetails(BaseModel):
    """Model for Fujifilm recipe details"""

    FilmSimulation: str = Field(default="Unknown")
    DynamicRange: str = Field(default="Unknown")
    GrainEffect: str = Field(default="Unknown")
    ColorChrome: str = Field(default="Unknown")
    ColorChromeBlue: str = Field(default="Unknown")
    WhiteBalance: str = Field(default="Unknown")
    WBShift: str = Field(default="Unknown")
    Highlights: str = Field(default="Unknown")
    Shadows: str = Field(default="Unknown")
    Color: str = Field(default="Unknown")
    Sharpness: str = Field(default="Unknown")
    NoiseReduction: str = Field(default="Unknown")


class FujiRecipeResponse(BaseModel):
    """Model for Fujifilm recipe response"""

    filename: str
    recipe: str
    recipe_details: RecipeDetails
    date: str = Field(default="Unknown Date")
    camera_model: str = Field(default="Unknown Camera")
    lens_model: str = Field(default="Unknown Lens")
    aperture: str = Field(default="Unknown")
    shutter_speed: str = Field(default="Unknown")
    iso: str = Field(default="Unknown")
    focal_length: str = Field(default="Unknown")


class BatchExifResponse(BaseModel):
    """Model for batch processing response"""

    results: List[ExifResponse]
    errors: List[Dict[str, str]] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    """Model for error responses"""

    detail: str
