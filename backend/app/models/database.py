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
        DATABASE_URL = os.getenv("DATABASE_URL")

        if not DATABASE_URL:
            raise RuntimeError("DATABASE_URL environment variable not set")

        _engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False
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
