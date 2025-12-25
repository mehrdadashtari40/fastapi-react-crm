# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Get DATABASE_URL from environment variable (set by docker-compose)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fallback for local development *without* Docker (if needed later)
    # Example: DATABASE_URL = "postgresql://yacrm_user:yacrm_pass@localhost:5432/yacrm_local"
    raise RuntimeError("DATABASE_URL environment variable is required")

# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    # pool_pre_ping=True, # Good for production/db reliability, less critical for local dev
    echo=True  # Optional: Logs SQL queries (helpful for debugging)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()