#!/usr/bin/env python3
"""
Add metadata column to tryon_history if missing (e.g. after deploy on existing DB).
Run from backend dir: python scripts/add_tryon_metadata_column.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    from sqlalchemy import text
    from app.models.database import get_engine

    engine = get_engine()
    url = str(engine.url)
    with engine.begin() as conn:
        if "postgresql" in url or "postgres" in url:
            conn.execute(text("ALTER TABLE tryon_history ADD COLUMN IF NOT EXISTS metadata JSONB"))
        else:
            try:
                conn.execute(text("ALTER TABLE tryon_history ADD COLUMN metadata TEXT"))
            except Exception as e:
                if "duplicate column" not in str(e).lower() and "already exists" not in str(e).lower():
                    raise
    print("Done: tryon_history.metadata column ensured.")

if __name__ == "__main__":
    main()
