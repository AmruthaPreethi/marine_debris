def confidence_level(confidence: float) -> str:
    return "HIGH" if confidence >= .80 else "MEDIUM" if confidence >= .60 else "LOW"

def risk_level(class_name: str, confidence: float) -> str:
    base = {"Ghost Net": 2, "Container": 2, "Metal Debris": 2, "Tire": 1, "Plastic Debris": 1, "Artificial Anomaly": 1}.get(class_name, 1)
    score = base + (1 if confidence >= .80 else 0)
    return "HIGH" if score >= 3 else "MEDIUM" if score == 2 else "LOW"
