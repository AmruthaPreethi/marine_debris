import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent
STORAGE_DIR = PROJECT_ROOT / "storage"
UPLOAD_DIR = STORAGE_DIR / "uploads"
PROCESSED_DIR = STORAGE_DIR / "processed"
ANNOTATED_DIR = STORAGE_DIR / "annotated"
REPORTS_DIR = STORAGE_DIR / "reports"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BACKEND_DIR / 'marine_debris.db'}")
MODEL_MODE = os.getenv("MODEL_MODE", "auto").lower()
# The trained project model is the normal inference model. Override MODEL_PATH for deployments.
MODEL_PATH = Path(os.getenv("MODEL_PATH", str(PROJECT_ROOT / "runs" / "detect" / "five_class" / "weights" / "best.pt")))
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", str(20 * 1024 * 1024)))
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}

def ensure_storage_directories() -> None:
    for directory in (UPLOAD_DIR, PROCESSED_DIR, ANNOTATED_DIR, REPORTS_DIR):
        directory.mkdir(parents=True, exist_ok=True)
