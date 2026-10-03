import logging
from pathlib import Path
from app.core.config import MODEL_MODE, MODEL_PATH
from app.services.demo_detector import DemoDetector

logger = logging.getLogger("uvicorn.error")

class YOLODetector:
    mode = "yolo"
    def __init__(self, model_path: Path):
        from ultralytics import YOLO
        self.model_path = model_path.resolve()
        self.model = YOLO(str(self.model_path))
        logger.info("MODEL PATH: %s", self.model_path)
        logger.info("MODEL CLASS NAMES: %s", dict(self.model.names))
    def detect(self, image):
        try:
            result = self.model(image, verbose=False)[0]
            detections = []
            for box in result.boxes:
                x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
                cls = int(box.cls[0].item())
                detections.append({"class_name": self.model.names[cls], "confidence": float(box.conf[0].item()), "bbox": [x1, y1, x2-x1, y2-y1]})
            logger.info("RAW YOLO DETECTIONS: %s", detections)
            return detections
        except Exception as exc:
            raise RuntimeError("Model inference failed.") from exc

def get_detector():
    if MODEL_MODE not in {"auto", "real", "demo"}:
        raise RuntimeError("MODEL_MODE must be auto, real, or demo.")
    if MODEL_MODE == "demo":
        return DemoDetector()
    try:
        if not MODEL_PATH.is_file():
            raise FileNotFoundError(f"YOLO weights were not found at {MODEL_PATH}.")
        return YOLODetector(MODEL_PATH)
    except Exception as exc:
        # Keep the prototype usable when weights are unavailable or incompatible.
        # The persisted model_mode remains "demo", so this is never presented as YOLO inference.
        logger.warning("Trained YOLO could not be loaded (%s); using DemoDetector.", exc)
        return DemoDetector()
