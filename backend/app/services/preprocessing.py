from pathlib import Path
import cv2
import numpy as np

def load_image(path: str | Path) -> np.ndarray:
    image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if image is None or image.size == 0:
        raise ValueError("The uploaded file is not a valid readable image.")
    return image

def denoise_sonar_image(image: np.ndarray) -> np.ndarray:
    return cv2.fastNlMeansDenoising(image, None, 8, 7, 21)

def enhance_contrast(image: np.ndarray) -> np.ndarray:
    return cv2.equalizeHist(image)

def apply_clahe(image: np.ndarray) -> np.ndarray:
    return cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(image)

def normalize_image(image: np.ndarray) -> np.ndarray:
    return cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

def preprocess_sonar_image(input_path: str | Path, output_path: str | Path) -> np.ndarray:
    image = load_image(input_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    if gray.dtype != np.uint8:
        gray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    processed = normalize_image(apply_clahe(enhance_contrast(denoise_sonar_image(gray))))
    if not cv2.imwrite(str(output_path), processed):
        raise ValueError("Unable to save processed image.")
    return processed
