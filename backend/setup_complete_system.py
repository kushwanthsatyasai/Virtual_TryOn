"""
Quick Setup Script for Complete System
======================================
Installs dependencies, creates database, tests everything
"""
import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and print status"""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ Success!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed!")
        if e.stderr:
            print(e.stderr)
        return False

def main():
    print("\n" + "="*60)
    print("🚀 COMPLETE VIRTUAL TRY-ON SYSTEM SETUP")
    print("="*60)
    print("\nThis will:")
    print("1. Install all required Python packages")
    print("2. Create the database with all tables")
    print("3. Test the system")
    print("\nPress Enter to continue...")
    input()
    
    # Step 1: Install dependencies
    packages = [
        "sqlalchemy",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-multipart"
    ]
    
    for package in packages:
        run_command(
            f"pip install {package}",
            f"Installing {package}"
        )
    
    # Step 2: Create database
    print(f"\n{'='*60}")
    print("🗄️ Creating Database")
    print("="*60)
    
    try:
        from app.models.database import Base, engine
        Base.metadata.create_all(bind=engine)
        print("✅ Database created successfully!")
        print("\nTables created:")
        for table in Base.metadata.tables.keys():
            print(f"  - {table}")
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        return
    
    # Step 3: Test imports
    print(f"\n{'='*60}")
    print("🧪 Testing Imports")
    print("="*60)
    
    try:
        from app.services.auth_service import AuthService
        from app.services.size_recommendation_service import SizeRecommendationService
        print("✅ All services imported successfully!")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return
    
    # Step 4: Create test user
    print(f"\n{'='*60}")
    print("👤 Creating Test User")
    print("="*60)
    
    try:
        from app.models.database import SessionLocal
        from app.models.user import User
        from app.services.auth_service import AuthService
        
        db = SessionLocal()
        auth = AuthService()
        
        # Check if test user exists
        existing = db.query(User).filter(User.username == "testuser").first()
        
        if existing:
            print("ℹ️  Test user already exists")
        else:
            test_user = User(
                email="test@example.com",
                username="testuser",
                hashed_password=auth.get_password_hash("Test1234!"),
                full_name="Test User"
            )
            db.add(test_user)
            db.commit()
            print("✅ Test user created!")
            print("   Username: testuser")
            print("   Password: Test1234!")
        
        db.close()
    except Exception as e:
        print(f"⚠️  Could not create test user: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    
    print("\n✅ System is ready!")
    print("\n📚 Next Steps:")
    print("\n1. Start the API server:")
    print("   python complete_api.py")
    print("\n2. Open API docs:")
    print("   http://localhost:8000/docs")
    print("\n3. Test authentication:")
    print("   Username: testuser")
    print("   Password: Test1234!")
    print("\n4. Read the guides:")
    print("   - ALL_FEATURES_READY.md")
    print("   - COMPLETE_IMPLEMENTATION_GUIDE.md")
    print("\n5. Integrate with Flutter:")
    print("   - Copy code from COMPLETE_IMPLEMENTATION_GUIDE.md")
    
    print(f"\n{'='*60}")
    print("🚀 Happy coding!")
    print("="*60)

if __name__ == "__main__":
    main()
