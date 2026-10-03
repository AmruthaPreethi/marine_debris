import logging
import hashlib
from pathlib import Path
import cv2
from sqlalchemy.orm import Session
from app.models.database_models import Analysis, Detection
from app.services.detector import get_detector
from app.services.preprocessing import load_image, preprocess_sonar_image
from app.services.risk_engine import confidence_level, risk_level

logger = logging.getLogger("uvicorn.error")

DEMO_SURVEY_CENTER = (18.5204, 72.8760)
DEMO_COORDINATE_SPAN = 0.004

def resolve_location(latitude: float | None, longitude: float | None, survey_id: str | None,
                     filename: str) -> tuple[float, float, str]:
    if latitude is not None and longitude is not None:
        return latitude, longitude, "user_provided"

    # Synthetic demo points stay near one documented demo survey center. The key
    # keeps files from the same survey geographically close and repeatable.
    key = survey_id or filename
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    latitude_offset = ((int.from_bytes(digest[:4], "big") / 2**32) * 2 - 1) * DEMO_COORDINATE_SPAN
    longitude_offset = ((int.from_bytes(digest[4:8], "big") / 2**32) * 2 - 1) * DEMO_COORDINATE_SPAN
    return DEMO_SURVEY_CENTER[0] + latitude_offset, DEMO_SURVEY_CENTER[1] + longitude_offset, "synthetic_demo"

def annotate_image(image, detections, output_path: Path) -> None:
    canvas = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR) if image.ndim == 2 else image.copy()
    for index, detection in enumerate(detections, 1):
        x, y, width, height = detection["bbox"]
        cv2.rectangle(canvas, (x, y), (x + width, y + height), (0, 220, 0), 2)
        label = f"#{index:02d} {detection['class_name']} {detection['confidence']:.0%}"
        cv2.putText(canvas, label, (x, max(18, y - 7)), cv2.FONT_HERSHEY_SIMPLEX, .45, (0, 220, 0), 1, cv2.LINE_AA)
    if not cv2.imwrite(str(output_path), canvas):
        raise ValueError("Unable to save annotated image.")

def run_analysis(db: Session, *, filename: str, original_path: Path, processed_path: Path, annotated_path: Path,
                 threshold: float, latitude: float | None, longitude: float | None, survey_id: str | None,
                 mission_id: str | None, depth: float | None) -> tuple[Analysis, int]:
    logger.info("UPLOADED IMAGE: %s", original_path.resolve())
    processed = preprocess_sonar_image(original_path, processed_path)
    detector = get_detector()
    # Preserve the processed image for review/annotation, but infer from the untouched
    # uploaded pixels so the trained model receives the same image it was validated on.
    raw = detector.detect(load_image(original_path))
    filtered = [item for item in raw if item["confidence"] >= threshold]
    annotate_image(processed, filtered, annotated_path)
    resolved_latitude, resolved_longitude, location_source = resolve_location(latitude, longitude, survey_id, filename)
    analysis = Analysis(filename=filename, model_mode=detector.mode, confidence_threshold=threshold,
                        original_image_path=str(original_path), processed_image_path=str(processed_path),
                        annotated_image_path=str(annotated_path), latitude=resolved_latitude, longitude=resolved_longitude,
                        location_source=location_source,
                        survey_id=survey_id, mission_id=mission_id, depth=depth)
    db.add(analysis); db.flush()
    for item in filtered:
        x, y, width, height = item["bbox"]
        db.add(Detection(analysis_id=analysis.id, class_name=item["class_name"], confidence=item["confidence"],
                         x=x, y=y, width=width, height=height, confidence_level=confidence_level(item["confidence"]),
                         risk_level=risk_level(item["class_name"], item["confidence"])))
    db.commit(); db.refresh(analysis)
    return analysis, len(raw)
