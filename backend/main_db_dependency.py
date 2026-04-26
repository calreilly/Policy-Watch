from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base
import os

DATABASE_URL = "sqlite:///./policywatch.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# For imports in other files
os.environ.setdefault("DATABASE_URL", DATABASE_URL)
