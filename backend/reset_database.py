"""
Reset database - drops all tables and recreates them
"""
from sqlalchemy import text
from app.models.database import get_engine, Base
from app.models import *

def reset_database():
    print("Resetting database...")
    
    engine = get_engine()
    
    # Drop all tables with CASCADE (PostgreSQL only)
    print("1. Dropping all tables with CASCADE...")
    with engine.connect() as conn:
        # Check if PostgreSQL (has schema public)
        db_url = str(engine.url)
        if db_url.startswith("postgresql"):
            conn.execute(text("DROP SCHEMA public CASCADE"))
            conn.execute(text("CREATE SCHEMA public"))
            conn.commit()
        else:
            # SQLite: drop all tables
            Base.metadata.drop_all(bind=engine)
    
    print("2. Creating all tables...")
    Base.metadata.create_all(bind=engine)
    
    print("\nDatabase reset complete!")
    print("All tables have been recreated with the latest schema.")
    print("\nYou can now:")
    print("1. Register a new user via API")
    print("2. Or run: python scripts/seed_data.py (if it exists)")

if __name__ == "__main__":
    reset_database()
