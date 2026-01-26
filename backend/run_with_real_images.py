"""
Run Virtual Try-On with Real Test Images
=========================================
Uses: test_images/test_user.png and test_images/test_cloth.png
"""

import asyncio
import os
import sys

# Fix Windows encoding for emojis
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# Ensure we're in the backend directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
sys.path.insert(0, script_dir)

async def main():
    print("\n" + "=" * 70)
    print("🎨 Virtual Try-On Pipeline - Real Images Test")
    print("=" * 70)
    print()
    
    from app.services.ai_service import AIService
    from app.core.config import settings
    
    # Use existing test images
    user_path = "test_images/test_user.png"
    cloth_path = "test_images/test_cloth.png"
    
    print("📸 Input Images:")
    print(f"   User:  {user_path}")
    print(f"   Cloth: {cloth_path}")
    print()
    
    # Check if they exist
    if not os.path.exists(user_path):
        print(f"❌ ERROR: {user_path} not found!")
        return
    if not os.path.exists(cloth_path):
        print(f"❌ ERROR: {cloth_path} not found!")
        return
    
    # Initialize AI service
    print("🔧 Initializing AI Service...")
    ai_service = AIService()
    print("   ✅ Service ready")
    print()
    
    # Ensure directories exist
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    os.makedirs(settings.INTERMEDIATE_DIR, exist_ok=True)
    
    # Run pipeline
    print("🚀 Running Pipeline (This may take 30-60 seconds)...")
    print()
    
    output_path = os.path.join(settings.OUTPUT_DIR, "real_tryon.png")
    
    success = await ai_service.generate_tryon(
        user_image_path=user_path,
        cloth_image_path=cloth_path,
        output_path=output_path
    )
    
    print()
    if success:
        print("=" * 70)
        print("✅ SUCCESS!")
        print("=" * 70)
        print()
        print("📂 Results:")
        print(f"   Final: {output_path}")
        print(f"   Stages: {settings.INTERMEDIATE_DIR}/")
        print()
    else:
        print("=" * 70)
        print("❌ FAILED")
        print("=" * 70)
        print()

if __name__ == "__main__":
    asyncio.run(main())

