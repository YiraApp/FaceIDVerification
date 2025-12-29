from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from app.models import VerificationResponse, StatusResponse, ModelInfoResponse
from app.services.face_verification import face_service
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("Starting Face ID Verification API...")
    try:
        face_service.initialize_model()
        logger.info("Model loaded successfully!")
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Face ID Verification API...")


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API for verifying face identity from PDF documents containing ID and selfie images",
    lifespan=lifespan
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Face ID Verification API",
        "version": settings.app_version,
        "docs": "/docs",
        "status": "/status"
    }


@app.get("/status", response_model=StatusResponse, tags=["Status"])
async def check_status():
    """Check status endpoint"""
    return StatusResponse(
        status="healthy" if face_service.model_loaded else "unhealthy",
        model_loaded=face_service.model_loaded,
        message="Service is running" if face_service.model_loaded else "Model not loaded"
    )


@app.get("/model-info", response_model=ModelInfoResponse, tags=["Info"])
async def model_info():
    """Get model information"""
    if not face_service.model_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    return ModelInfoResponse(
        model_name=settings.model_name,
        detection_size=settings.detection_size,
        backend="GPU" if settings.ctx_id >= 0 else "CPU"
    )


@app.post("/api/verify-face", response_model=VerificationResponse, tags=["Verification"])
async def verify_face(
    file: UploadFile = File(..., description="PDF file containing ID photo and selfie (2 pages minimum)")
):
    """
    Verify face identity from PDF document
    
    Upload a PDF containing:
    - Page 1: ID document with photo
    - Page 2: Selfie image
    
    The API will extract faces from both pages and compare them.
    
    Returns:
    - status: SUCCESS or FAILED
    - match: True if faces match, False otherwise
    - confidence: Confidence score (0-100)
    - similarity: Cosine similarity score (0-1)
    - quality_1, quality_2: Quality scores for each face
    - threshold_used: Similarity threshold applied
    - reason: Error message if verification failed
    """
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    try:
        # Read file content
        pdf_bytes = await file.read()
        
        # Validate file size
        if len(pdf_bytes) > settings.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {settings.max_file_size / (1024*1024)}MB"
            )
        
        # Perform face verification
        logger.info(f"Processing file: {file.filename}")
        result = face_service.compare_faces_from_pdf(pdf_bytes)
        
        # Return appropriate status code
        if result["status"] == "FAILED":
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=result
            )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
