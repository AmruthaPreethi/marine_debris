class DemoDetector:
    """Deterministic visual placeholder, not a trained AI model."""
    mode = "demo"
    def detect(self, image):
        height, width = image.shape[:2]
        return [
            {"class_name": "Ghost Net", "confidence": 0.91, "bbox": [width // 8, height // 6, max(20, width // 3), max(20, height // 4)]},
            {"class_name": "Other Debris", "confidence": 0.67, "bbox": [width // 2, height // 2, max(20, width // 5), max(20, height // 6)]},
            {"class_name": "Artificial Anomaly", "confidence": 0.48, "bbox": [width * 2 // 3, height // 5, max(20, width // 6), max(20, height // 5)]},
        ]
