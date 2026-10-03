import json
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from app.models.database_models import Analysis

DISCLAIMER = "AI-assisted detection. Results require human verification before operational decisions."

def report_data(analysis: Analysis) -> dict:
    return {"analysis_id": analysis.id, "filename": analysis.filename, "date_time": analysis.created_at.isoformat(),
            "survey_id": analysis.survey_id, "mission_id": analysis.mission_id, "latitude": analysis.latitude,
            "longitude": analysis.longitude, "location_source": analysis.location_source, "depth": analysis.depth, "model_mode": analysis.model_mode,
            "confidence_threshold": analysis.confidence_threshold, "disclaimer": DISCLAIMER,
            "detections": [{"id": d.id, "class": d.class_name, "confidence": d.confidence,
                            "confidence_level": d.confidence_level, "risk_level": d.risk_level,
                            "bounding_box": [d.x, d.y, d.width, d.height]} for d in analysis.detections]}

def generate_json(analysis: Analysis, path: Path) -> Path:
    path.write_text(json.dumps(report_data(analysis), indent=2), encoding="utf-8")
    return path

def generate_pdf(analysis: Analysis, path: Path) -> Path:
    data = report_data(analysis); pdf = canvas.Canvas(str(path), pagesize=A4); _, h = A4; y = h - 48
    lines = ["Marine Debris Detection Report", f"Analysis ID: {data['analysis_id']}", f"Filename: {data['filename']}",
             f"Date/time: {data['date_time']}", f"Survey ID: {data['survey_id'] or 'N/A'}", f"Mission ID: {data['mission_id'] or 'N/A'}",
             f"Latitude / Longitude: {data['latitude'] if data['latitude'] is not None else 'N/A'} / {data['longitude'] if data['longitude'] is not None else 'N/A'}",
             f"Location source: {data['location_source'] or 'N/A'}",
             f"Depth: {data['depth'] if data['depth'] is not None else 'N/A'}", f"Model mode: {data['model_mode']}",
             f"Confidence threshold: {data['confidence_threshold']:.0%}", "Detection summary:"]
    lines += [f"#{d['id']} | {d['class']} | {d['confidence']:.0%} | {d['confidence_level']} | {d['risk_level']} | {d['bounding_box']}" for d in data['detections']]
    lines.append(DISCLAIMER)
    for line in lines:
        if y < 45: pdf.showPage(); y = h - 48
        pdf.drawString(40, y, line[:130]); y -= 18
    pdf.save(); return path
