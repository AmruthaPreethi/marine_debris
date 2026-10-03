from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import DATABASE_URL

class Base(DeclarativeBase):
    pass

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def ensure_analysis_location_source_column() -> None:
    if "location_source" in {column["name"] for column in inspect(engine).get_columns("analyses")}:
        return
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE analyses ADD COLUMN location_source VARCHAR(30)"))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
