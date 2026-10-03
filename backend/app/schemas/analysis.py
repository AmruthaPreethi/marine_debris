from datetime import datetime
from pydantic import BaseModel

class DetectionOut(BaseModel):
    id: int
    class_name: str
    confidence: float
    bbox: list[int]
    confidence_level: str
    risk_level: str

class AnalysisOut(BaseModel):
    id: int
    filename: str
    created_at: datetime
    status: str
    model_mode: str
    confidence_threshold: float
    latitude: float | None
    longitude: float | None
    location_source: str | None
    location: str
    survey_id: str | None
    mission_id: str | None
    depth: float | None
    timestamp: datetime
    original_image_path: str
    processed_image_path: str
    annotated_image_path: str
    detections: list[DetectionOut]
