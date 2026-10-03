from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session, selectinload
from app.core.config import ALLOWED_EXTENSIONS, ANNOTATED_DIR, MAX_UPLOAD_SIZE, PROCESSED_DIR, UPLOAD_DIR
from app.db.database import get_db
from app.models.database_models import Analysis
from app.services.analysis_service import run_analysis

router = APIRouter(prefix="/api", tags=["analysis"])

def serialize(analysis):
    return {"id": analysis.id, "filename": analysis.filename, "created_at": analysis.created_at, "status": analysis.status,
            "model_mode": analysis.model_mode, "confidence_threshold": analysis.confidence_threshold, "latitude": analysis.latitude,
            "longitude": analysis.longitude, "location_source": analysis.location_source,
            "location": "Location unavailable" if analysis.latitude is None or analysis.longitude is None else {"latitude": analysis.latitude, "longitude": analysis.longitude},
            "survey_id": analysis.survey_id, "mission_id": analysis.mission_id, "depth": analysis.depth, "timestamp": analysis.timestamp,
            "original_image_path": analysis.original_image_path, "processed_image_path": analysis.processed_image_path,
            "annotated_image_path": analysis.annotated_image_path, "detections": [{"id": d.id, "class_name": d.class_name, "confidence": d.confidence, "bbox": [d.x,d.y,d.width,d.height], "confidence_level": d.confidence_level, "risk_level": d.risk_level} for d in analysis.detections]}

@router.post("/analyze")
async def analyze(image: UploadFile = File(...), confidence_threshold: float = Form(.60), latitude: float | None = Form(None), longitude: float | None = Form(None), survey_id: str | None = Form(None), mission_id: str | None = Form(None), depth: float | None = Form(None), db: Session = Depends(get_db)):
    suffix = Path(image.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS: raise HTTPException(415, "Supported files are PNG, JPG, JPEG, and TIFF.")
    if not 0 <= confidence_threshold <= 1: raise HTTPException(422, "confidence_threshold must be between 0 and 1.")
    if (latitude is None) != (longitude is None): raise HTTPException(422, "Latitude and longitude must be supplied together.")
    if latitude is not None and not -90 <= latitude <= 90: raise HTTPException(422, "Invalid latitude.")
    if longitude is not None and not -180 <= longitude <= 180: raise HTTPException(422, "Invalid longitude.")
    content = await image.read()
    if not content: raise HTTPException(422, "Image file is empty.")
    if len(content) > MAX_UPLOAD_SIZE: raise HTTPException(413, "Image exceeds the maximum upload size.")
    token = uuid4().hex; original = UPLOAD_DIR / f"{token}{suffix}"; original.write_bytes(content)
    try:
        analysis, raw_count = run_analysis(db, filename=Path(image.filename).name, original_path=original,
            processed_path=PROCESSED_DIR / f"{token}.png", annotated_path=ANNOTATED_DIR / f"{token}.png", threshold=confidence_threshold,
            latitude=latitude, longitude=longitude, survey_id=survey_id, mission_id=mission_id, depth=depth)
        db.refresh(analysis, ["detections"])
        result = serialize(analysis); result.update(raw_detection_count=raw_count, filtered_detection_count=len(analysis.detections)); return result
    except (ValueError, FileNotFoundError, RuntimeError) as exc:
        db.rollback(); raise HTTPException(422 if isinstance(exc, ValueError) else 503, str(exc)) from None
    except Exception:
        db.rollback(); raise HTTPException(500, "Analysis could not be completed.") from None

@router.get("/analyses")
def analyses(db: Session = Depends(get_db)):
    rows = db.query(Analysis).options(selectinload(Analysis.detections)).order_by(Analysis.created_at.desc()).all()
    return [serialize(row) for row in rows]

@router.get("/analyses/{analysis_id}")
def analysis_detail(analysis_id: int, db: Session = Depends(get_db)):
    row = db.query(Analysis).options(selectinload(Analysis.detections)).filter(Analysis.id == analysis_id).first()
    if not row: raise HTTPException(404, "Analysis not found.")
    return serialize(row)
