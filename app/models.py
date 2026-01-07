from pydantic import BaseModel, Field
from typing import Optional, Literal


class VerificationData(BaseModel):
    """Data model for face verification results"""
    status: Literal["SUCCESS", "FAILED"]
    match: Optional[bool] = None
    confidence: Optional[float] = Field(None, description="Confidence percentage (0-100)")
    confidence_level: Optional[Literal["HIGH", "MEDIUM", "LOW", "NO_MATCH"]] = Field(None, description="Confidence level category")
    requires_manual_review: Optional[bool] = Field(None, description="Whether manual review is recommended")
    similarity: Optional[float] = Field(None, description="Cosine similarity score (0-1)")
    quality_1: Optional[int] = Field(None, description="Quality score for first face (0-100)")
    quality_2: Optional[int] = Field(None, description="Quality score for second face (0-100)")
    threshold_used: Optional[float] = Field(None, description="Similarity threshold applied")
    processing_time_seconds: Optional[float] = Field(None, description="Total processing time in seconds")
    reason: Optional[str] = Field(None, description="Failure reason if status is FAILED")
    
    model_config = {
        "exclude_none": True,  # Exclude None/null values from response
    }


class ApiResponse(BaseModel):
    """Standardized API response wrapper"""
    status: bool = Field(..., description="Whether the API executed successfully")
    message: str = Field(..., description="Success or error message")
    data: Optional[VerificationData] = Field(None, description="Verification data (only present on success)")


class StatusResponse(BaseModel):
    """Status check response"""
    status: str
    model_loaded: bool
    message: str


class ModelInfoResponse(BaseModel):
    """Model information response"""
    model_name: str
    detection_size: tuple
    backend: str
