import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    app_name: str = "Face ID Verification API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Model Settings
    model_name: str = "buffalo_l"
    detection_size: tuple = (640, 640)
    ctx_id: int = 0  # -1 for CPU, 0 for GPU
    
    # File Upload Settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: list = [".pdf"]
    
    # Face Detection Settings
    rotation_angles: list = [0, -10, 10, -20, 20, -30, 30]
    min_quality_threshold: int = 25
    high_quality_threshold: int = 60
    low_quality_threshold: int = 70
    high_similarity_threshold: float = 0.33
    default_similarity_threshold: float = 0.45
    
    # Random Confidence Settings (for testing)
    use_random_confidence: bool = True
    random_confidence_match_min: float = 70.0
    random_confidence_match_max: float = 85.0
    random_confidence_no_match_min: float = 30.0
    random_confidence_no_match_max: float = 45.0
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
