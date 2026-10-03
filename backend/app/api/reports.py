from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, selectinload
from app.core.config import REPORTS_DIR
from app.db.database import get_db
from app.models.database_models import Analysis
from app.services.report_generator import generate_json, generate_pdf

router = APIRouter(prefix="/api/reports", tags=["reports"])
@router.get("/{analysis_id}/{format}")
def report(analysis_id: int, format: str, db: Session = Depends(get_db)):
    analysis = db.query(Analysis).options(selectinload(Analysis.detections)).filter(Analysis.id == analysis_id).first()
    if not analysis: raise HTTPException(404, "Analysis not found.")
    if format not in {"pdf", "json"}: raise HTTPException(422, "Report format must be pdf or json.")
    path = REPORTS_DIR / f"analysis_{analysis_id}.{format}"
    try:
        (generate_pdf if format == "pdf" else generate_json)(analysis, path)
    except Exception:
        raise HTTPException(500, "Report generation failed.") from None
    return FileResponse(path, media_type="application/pdf" if format == "pdf" else "application/json", filename=path.name)
