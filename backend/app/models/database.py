"""
Database Configuration (Render-safe)
===================================
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Base class for models
Base = declarative_base()

# Lazy globals
_engine = None
_SessionLocal = None


def get_engine():
    """
    Create engine lazily to avoid import-time crashes on Render
    """
    global _engine, _SessionLocal

    if _engine is None:
        # Try environment variable first, then fall back to settings default
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        if not DATABASE_URL:
            # Lazy import to avoid circular dependencies
            from app.core.config import settings
            DATABASE_URL = settings.DATABASE_URL
        
        if not DATABASE_URL:
            raise RuntimeError("DATABASE_URL not set in environment or config")

        # SQLite-specific configuration
        connect_args = {}
        if DATABASE_URL.startswith("sqlite"):
            connect_args = {"check_same_thread": False}
        
        _engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False,
            connect_args=connect_args
        )

        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=_engine
        )

    return _engine


def get_db():
    """
    FastAPI DB dependency
    """
    get_engine()
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()
