#!/usr/bin/env python3
"""
Database initialization script.
Creates all tables and sets up the database schema.
"""

import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base
from app.models import User, Cloth, TryonResult

def init_database():
    """Initialize the database by creating all tables."""
    print("Creating database tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Create directories for file uploads
        os.makedirs("static/uploads", exist_ok=True)
        os.makedirs("static/generated_outputs", exist_ok=True)
        print("✅ Upload directories created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()