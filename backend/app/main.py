from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect
from app.api import analysis, auth, reports, statistics
from app.core.config import STORAGE_DIR, ensure_storage_directories
from app.core.security import hash_password
from app.db.database import Base, SessionLocal, engine, ensure_analysis_location_source_column
from app.models.database_models import User

@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_storage_directories()
    if inspect(engine).has_table("analyses"):
        ensure_analysis_location_source_column()
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "admin").first():
            db.add(User(username="admin", email="admin@example.local", password_hash=hash_password("admin123"))); db.commit()
    finally: db.close()
    yield

app = FastAPI(title="Marine Debris Detection API", lifespan=lifespan)
_default_origins = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173"
_frontend_url = os.getenv("FRONTEND_URL", "").strip()
_cors_env = os.getenv("CORS_ORIGINS", _default_origins)
cors_origins = [o.strip() for o in _cors_env.split(",") if o.strip()]
if _frontend_url and _frontend_url not in cors_origins:
    cors_origins.append(_frontend_url)
app.add_middleware(CORSMiddleware, allow_origins=cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/storage", StaticFiles(directory=STORAGE_DIR), name="storage")
app.include_router(auth.router); app.include_router(analysis.router); app.include_router(statistics.router); app.include_router(reports.router)

@app.get("/api/health")
def health(): return {"status": "ok"}
