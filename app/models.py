from pydantic import BaseModel, Field
from typing import Optional, Literal


class VerificationResponse(BaseModel):
    """Response model for face verification"""
    status: Literal["SUCCESS", "FAILED"]
    match: Optional[bool] = None
    confidence: Optional[float] = Field(None, description="Confidence percentage (0-100)")
    similarity: Optional[float] = Field(None, description="Cosine similarity score (0-1)")
    quality_1: Optional[int] = Field(None, description="Quality score for first face (0-100)")
    quality_2: Optional[int] = Field(None, description="Quality score for second face (0-100)")
    threshold_used: Optional[float] = Field(None, description="Similarity threshold applied")
    reason: Optional[str] = Field(None, description="Failure reason if status is FAILED")


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
