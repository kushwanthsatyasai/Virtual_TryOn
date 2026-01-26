"""
Test script for Gradio Space Virtual Try-On
Uses frogleo/AI-Clothes-Changer Space
"""
import sys
import codecs
from pathlib import Path

# Fix Windows encoding for emojis
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

from app.services.gradio_vton_service import GradioVTONService
from app.core.config import settings

def main():
    print("=" * 70)
    print("Virtual Try-On using Gradio Space")
    print("=" * 70)
    print(f"\nSpace: {settings.GRADIO_SPACE_NAME}")
    print(f"HF Token: {'✓ Set' if settings.HF_TOKEN else '✗ Not set'}")
    
    # Test images
    person_image = "test_images/test_user.png"
    cloth_image = "test_images/test_cloth.png"
    output_image = "static/generated_outputs/gradio_tryon_result.png"
    
    print(f"\nInput Images:")
    print(f"  Person: {person_image}")
    print(f"  Cloth:  {cloth_image}")
    print(f"\nOutput:")
    print(f"  Result: {output_image}")
    
    # Initialize service
    print(f"\n{'='*70}")
    print("Initializing Gradio VTO Service...")
    print(f"{'='*70}")
    
    try:
        service = GradioVTONService()
        
        # Health check
        if service.health_check():
            print("✓ Space is accessible")
        else:
            print("✗ Space health check failed")
            return
        
        # Generate try-on
        print(f"\n{'='*70}")
        print("Generating Virtual Try-On...")
        print(f"{'='*70}")
        
        result = service.generate_tryon(
            person_image_path=person_image,
            cloth_image_path=cloth_image,
            output_path=output_image,
            denoise_steps=settings.VTON_DENOISE_STEPS,
            seed=settings.VTON_SEED
        )
        
        print(f"\n{'='*70}")
        print("✓ SUCCESS!")
        print(f"{'='*70}")
        print(f"\nGenerated image: {result}")
        print("\nOpen the image to see the result!")
        
    except Exception as e:
        print(f"\n{'='*70}")
        print("✗ ERROR")
        print(f"{'='*70}")
        print(f"\n{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
