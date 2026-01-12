from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
import logging
import time
import asyncio
from contextlib import asynccontextmanager

from app.models import ApiResponse, VerificationData, StatusResponse, ModelInfoResponse
from app.services.face_verification import face_service
from app.config import settings

# --------------------------------------------------
# Logging Configuration
# --------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# Concurrency Control (CRITICAL)
# --------------------------------------------------
# Matches Azure Container Apps:
# concurrentRequests = 1
MAX_CONCURRENT_JOBS = 1
semaphore = asyncio.Semaphore(MAX_CONCURRENT_JOBS)

# --------------------------------------------------
# Lifespan (Startup / Shutdown)
# --------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Face ID Verification API...")
    try:
        face_service.initialize_model()
        logger.info("InsightFace model loaded successfully")
    except Exception as e:
        logger.error(f"Model initialization failed: {e}")
        raise

    yield

    logger.info("Shutting down Face ID Verification API...")

# --------------------------------------------------
# FastAPI App
# --------------------------------------------------
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API for verifying face identity from PDF documents",
    lifespan=lifespan
)

# --------------------------------------------------
# Health Endpoints
# --------------------------------------------------
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Face ID Verification API",
        "version": settings.app_version,
        "docs": "/docs",
        "status": "/status"
    }

@app.get("/status", response_model=StatusResponse, tags=["Status"])
async def check_status():
    return StatusResponse(
        status="healthy" if face_service.model_loaded else "unhealthy",
        model_loaded=face_service.model_loaded,
        message="Service is running" if face_service.model_loaded else "Model not loaded"
    )

@app.get("/model-info", response_model=ModelInfoResponse, tags=["Info"])
async def model_info():
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

# --------------------------------------------------
# Main Verification API
# --------------------------------------------------
@app.post(
    "/api/verify-face",
    response_model=ApiResponse,
    response_model_exclude_none=True,
    tags=["Verification"]
)
async def verify_face(
    file: UploadFile = File(..., description="PDF file containing ID photo and selfie")
):
    start_time = time.time()

    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        return ApiResponse(
            status=False,
            message="Only PDF files are allowed",
            data=None
        )

    try:
        # Read PDF
        pdf_bytes = await file.read()

        # Validate size
        if len(pdf_bytes) > settings.max_file_size:
            return ApiResponse(
                status=False,
                message=f"File size exceeds {settings.max_file_size / (1024 * 1024)} MB",
                data=None
            )

        logger.info(f"Processing file: {file.filename}")

        # --------------------------------------------------
        # CRITICAL SECTION (CPU-BOUND INSIGHTFACE)
        # --------------------------------------------------
        async with semaphore:
            result = await run_in_threadpool(
                face_service.compare_faces_from_pdf,
                pdf_bytes
            )

        # Processing time
        processing_time = round(time.time() - start_time, 2)
        result["processing_time_seconds"] = processing_time

        logger.info(f"Processing completed in {processing_time}s")

        # Remove None values
        filtered_result = {k: v for k, v in result.items() if v is not None}

        verification_data = VerificationData(**filtered_result)

        return ApiResponse(
            status=True,
            message="success",
            data=verification_data
        )

    except Exception as e:
        logger.exception("Error during face verification")
        return ApiResponse(
            status=False,
            message=f"Internal server error: {str(e)}",
            data=None
        )

# --------------------------------------------------
# Local Run
# --------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000
    )
