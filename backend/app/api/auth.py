from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import verify_password
from app.db.database import get_db
from app.models.database_models import User
from app.schemas.auth import LoginRequest

router = APIRouter(prefix="/api/auth", tags=["auth"])
@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    return {"message": "Login successful", "username": user.username}
