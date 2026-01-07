import cv2
import io
import numpy as np
from insightface.app import FaceAnalysis
from numpy.linalg import norm
import fitz
import logging
from typing import Optional, Dict, Any, List, Tuple

from app.config import settings

logger = logging.getLogger(__name__)


class FaceVerificationService:
    """Service class for face verification operations"""
    
    def __init__(self):
        self.app: Optional[FaceAnalysis] = None
        self.model_loaded = False
    
    def initialize_model(self):
        """Initialize the InsightFace model"""
        try:
            logger.info("Initializing Face Analysis Model...")
            self.app = FaceAnalysis(name=settings.model_name)
            self.app.prepare(ctx_id=settings.ctx_id, det_size=settings.detection_size)
            self.model_loaded = True
            logger.info("Face Analysis Model initialized successfully!")
        except Exception as e:
            logger.error(f"Failed to initialize model: {str(e)}")
            raise
    
    def extract_images_from_pdf(self, pdf_bytes: bytes) -> List[np.ndarray]:
        """
        Extract images from PDF pages
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            List of images as numpy arrays
        """
        images = []
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            for page in doc:
                pix = page.get_pixmap(dpi=300)
                img_bytes = pix.tobytes("png")
                # Convert to numpy array
                nparr = np.frombuffer(img_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if img is not None:
                    images.append(img)
            doc.close()
            logger.info(f"Extracted {len(images)} images from PDF")
        except Exception as e:
            logger.error(f"Error extracting images from PDF: {str(e)}")
            raise
        
        return images
    
    def estimate_face_quality(self, face, img: np.ndarray) -> int:
        """
        Estimate face quality based on size and sharpness
        
        Args:
            face: Detected face object
            img: Image containing the face
            
        Returns:
            Quality score (0-100)
        """
        x1, y1, x2, y2 = map(int, face.bbox)
        crop = img[y1:y2, x1:x2]
        
        if crop.size == 0:
            return 0
        
        # Convert to grayscale for blur detection
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        blur = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Size score
        size_score = min(1.0, (crop.shape[0] * crop.shape[1]) / (150 * 150))
        
        # Blur score
        blur_score = min(1.0, blur / 120)
        
        # Combined quality score
        quality = int((0.6 * size_score + 0.4 * blur_score) * 100)
        
        return quality
    
    def get_document_embedding(self, img: np.ndarray) -> Tuple[Optional[np.ndarray], int, Optional[Any], Optional[np.ndarray]]:
        """
        Extract face embedding from document image with rotation handling
        
        Args:
            img: Input image as numpy array
            
        Returns:
            Tuple of (embedding, quality_score, face_object, rotated_image)
        """
        h, w = img.shape[:2]
        best_embedding = None
        best_quality = 0
        best_face = None
        best_img = None
        
        for angle in settings.rotation_angles:
            if angle != 0:
                M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
                test_img = cv2.warpAffine(
                    img, M, (w, h),
                    flags=cv2.INTER_LINEAR,
                    borderMode=cv2.BORDER_REPLICATE
                )
            else:
                test_img = img
            
            faces = self.app.get(test_img)
            if not faces:
                continue
            
            for face in faces:
                q = self.estimate_face_quality(face, test_img)
                if q > best_quality:
                    best_quality = q
                    best_face = face
                    best_embedding = face.embedding / norm(face.embedding)
                    best_img = test_img
        
        return best_embedding, best_quality, best_face, best_img
    
    def generate_random_confidence(self, match: bool) -> float:
        """
        Generate random confidence score based on match result
        
        Args:
            match: Whether faces match or not
            
        Returns:
            Random confidence score
        """
        if match:
            confidence = np.random.uniform(
                settings.random_confidence_match_min,
                settings.random_confidence_match_max
            )
        else:
            confidence = np.random.uniform(
                settings.random_confidence_no_match_min,
                settings.random_confidence_no_match_max
            )
        
        return round(confidence, 2)
    
    def compare_faces_from_pdf(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """
        Compare faces extracted from PDF
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            Dictionary containing verification results
        """
        if not self.model_loaded:
            return {
                "status": "FAILED",
                "reason": "Model not initialized"
            }
        
        try:
            # Extract images from PDF
            images = self.extract_images_from_pdf(pdf_bytes)
            
            if len(images) < 2:
                return {
                    "status": "FAILED",
                    "reason": f"PDF must contain at least 2 pages. Found {len(images)} page(s)"
                }
            
            results = []
            
            # Process each image to extract face embeddings
            for img in images:
                emb, q, face, rotated_img = self.get_document_embedding(img)
                if emb is not None and face is not None:
                    results.append({
                        "emb": emb,
                        "quality": q
                    })
                if len(results) >= 2:
                    break
            
            if len(results) < 2:
                return {
                    "status": "FAILED",
                    "reason": "Could not detect faces in both images. Ensure PDF contains clear face photos."
                }
            
            # Calculate similarity
            emb1, emb2 = results[0]["emb"], results[1]["emb"]
            similarity = float(np.dot(emb1, emb2))
            
            q1, q2 = results[0]["quality"], results[1]["quality"]
            low_q = min(q1, q2)
            high_q = max(q1, q2)
            
            # Quality check
            if low_q < settings.min_quality_threshold:
                return {
                    "status": "FAILED",
                    "reason": f"Face quality too low (minimum quality: {low_q}). Please provide clearer images."
                }
            
            # Adaptive threshold based on quality
            if high_q >= settings.high_quality_threshold and low_q < settings.low_quality_threshold:
                threshold = settings.high_similarity_threshold
            else:
                threshold = settings.default_similarity_threshold
            
            # Determine confidence level and manual review requirement
            confidence_level = None
            requires_manual_review = False
            match = False
            
            if similarity >= settings.high_confidence_threshold:
                # High confidence match
                match = True
                confidence_level = "HIGH"
                requires_manual_review = False
            elif similarity >= threshold:
                # Medium confidence match
                match = True
                confidence_level = "MEDIUM"
                requires_manual_review = False
            elif similarity >= (threshold - settings.tolerance_band):
                # Within tolerance band - recommend manual review
                match = True
                confidence_level = "LOW"
                requires_manual_review = True
            else:
                # No match
                match = False
                confidence_level = "NO_MATCH"
                requires_manual_review = False
            
            # Calculate confidence
            if settings.use_random_confidence:
                confidence = self.generate_random_confidence(match)
            else:
                confidence = round(similarity * 100, 2)
            
            return {
                "status": "SUCCESS",
                "quality_1": q1,
                "quality_2": q2,
                "similarity": round(similarity, 3),
                "threshold_used": threshold,
                "match": bool(match),
                "confidence": confidence,
                "confidence_level": confidence_level,
                "requires_manual_review": requires_manual_review
            }
        
        except Exception as e:
            logger.error(f"Error during face comparison: {str(e)}")
            return {
                "status": "FAILED",
                "reason": f"Processing error: {str(e)}"
            }


# Global service instance
face_service = FaceVerificationService()
