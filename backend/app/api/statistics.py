from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.database_models import Analysis, Detection

router = APIRouter(prefix="/api", tags=["statistics"])
@router.get("/statistics")
def statistics(db: Session = Depends(get_db)):
    by_class = dict(db.query(Detection.class_name, func.count(Detection.id)).group_by(Detection.class_name).all())
    by_risk = dict(db.query(Detection.risk_level, func.count(Detection.id)).group_by(Detection.risk_level).all())
    return {"analysis_count": db.query(func.count(Analysis.id)).scalar() or 0,
            "detection_count": db.query(func.count(Detection.id)).scalar() or 0,
            "detections_by_class": by_class, "detections_by_risk_level": by_risk}
