"""Database setup.

This module creates the SQLAlchemy engine and session factory used across the app.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import DATABASE_URL

# check_same_thread=False is needed for SQLite when the app is accessed by FastAPI.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# SessionLocal creates database sessions for each request or script run.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class used by all ORM models.
Base = declarative_base()


def get_db():
    """Yield a database session for FastAPI dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()