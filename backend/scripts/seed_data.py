#!/usr/bin/env python3
"""
Database seeding script.
Adds sample data for testing and development.
"""

import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.core.security import get_password_hash
from app.models import User, Cloth

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_database():
    """Seed the database with sample data."""
    db = SessionLocal()
    
    try:
        print("Seeding database with sample data...")
        
        # Create sample users
        users_data = [
            {
                "name": "John Doe",
                "email": "john@example.com",
                "password": "password123"
            },
            {
                "name": "Jane Smith",
                "email": "jane@example.com",
                "password": "password123"
            }
        ]
        
        for user_data in users_data:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing_user:
                user = User(
                    name=user_data["name"],
                    email=user_data["email"],
                    password_hash=get_password_hash(user_data["password"])
                )
                db.add(user)
                print(f"✅ Created user: {user_data['name']}")
        
        # Create sample clothes
        clothes_data = [
            {
                "name": "Blue Denim Jacket",
                "category": "jacket",
                "image_url": "/static/uploads/sample_jacket.jpg"
            },
            {
                "name": "White Cotton T-Shirt",
                "category": "shirt",
                "image_url": "/static/uploads/sample_tshirt.jpg"
            },
            {
                "name": "Black Formal Dress",
                "category": "dress",
                "image_url": "/static/uploads/sample_dress.jpg"
            }
        ]
        
        # Get first user to assign as uploader
        first_user = db.query(User).first()
        if first_user:
            for cloth_data in clothes_data:
                # Check if cloth already exists
                existing_cloth = db.query(Cloth).filter(Cloth.name == cloth_data["name"]).first()
                if not existing_cloth:
                    cloth = Cloth(
                        name=cloth_data["name"],
                        category=cloth_data["category"],
                        image_url=cloth_data["image_url"],
                        uploaded_by=first_user.id
                    )
                    db.add(cloth)
                    print(f"✅ Created cloth: {cloth_data['name']}")
        
        db.commit()
        print("✅ Database seeded successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()