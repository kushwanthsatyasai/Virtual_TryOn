"""
Download Virtual Try-On Model (Corrected)
==========================================
Downloads actual VTO model repositories (not Spaces).

Options:
1. IDM-VTON (recommended, works well)
2. OOTDiffusion (alternative)
3. LaDI-VTON (for loose clothing)
"""

import os
import sys
import time
from datetime import datetime, timedelta

# Fix Windows encoding
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


# Available VTO Models (actual model repositories, not Spaces)
VTO_MODELS = {
    "idm-vton": {
        "repo_id": "yisol/IDM-VTON",
        "name": "IDM-VTON",
        "size": "~8-10 GB",
        "description": "High-quality but has compatibility issues with standard diffusers",
        "recommended": False,
        "note": "Requires custom loading - not fully supported"
    },
    "ootdiffusion": {
        "repo_id": "levihsu/OOTDiffusion",
        "name": "OOTDiffusion",
        "size": "~5-7 GB",
        "description": "Works well with diffusers, good quality results",
        "recommended": True
    },
    "ladi-vton": {
        "repo_id": "levihsu/LaDI-VTON",
        "name": "LaDI-VTON",
        "size": "~6-8 GB",
        "description": "Good for loose clothing (dresses, jackets)",
        "recommended": False
    }
}


def download_vto_model(model_key: str = "idm-vton"):
    """
    Download a Virtual Try-On model
    
    Args:
        model_key: One of "idm-vton", "ootdiffusion", "ladi-vton"
    """
    
    if model_key not in VTO_MODELS:
        print(f"❌ Error: Unknown model '{model_key}'")
        print(f"   Available: {', '.join(VTO_MODELS.keys())}")
        return False
    
    model_info = VTO_MODELS[model_key]
    
    print("\n" + "="*70)
    print("📥 Virtual Try-On Model Downloader")
    print("="*70)
    print()
    
    # Import after encoding is fixed
    from huggingface_hub import snapshot_download, login
    from app.core.config import settings
    
    if not settings.HF_TOKEN:
        print("❌ Error: No HuggingFace token found!")
        print("   Please add HF_TOKEN to your .env file")
        return False
    
    # Login
    print("🔐 Logging in to HuggingFace...")
    try:
        login(token=settings.HF_TOKEN)
        print("✅ Authenticated successfully")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False
    
    # Model info
    repo_id = model_info["repo_id"]
    cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
    
    print()
    print("📊 Download Information:")
    print(f"   Model: {model_info['name']}")
    print(f"   Repository: {repo_id}")
    print(f"   Size: {model_info['size']}")
    print(f"   Description: {model_info['description']}")
    print(f"   Cache: {cache_dir}")
    print()
    
    if model_info.get("recommended"):
        print("⭐ This is the recommended model for best results")
        print()
    
    print("⏱️  Estimated Time:")
    print("   Fast connection (10 Mbps): ~2-3 hours")
    print("   Medium connection (2 Mbps): ~10-15 hours")
    print("   Slow connection (500 Kbps): ~40-50 hours")
    print()
    print("💡 Tips:")
    print("   • Keep laptop plugged in")
    print("   • Disable sleep mode")
    print("   • Press Ctrl+C to pause (can resume later)")
    print("   • Files are cached - won't re-download if interrupted")
    print()
    
    input("Press ENTER to start download... ")
    
    print()
    print("🚀 Starting download...")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    start_time = time.time()
    
    try:
        # Download MODEL repository (not Space)
        local_dir = snapshot_download(
            repo_id=repo_id,
            repo_type="model",  # Explicitly specify model type
            resume_download=True,
            local_files_only=False,
            token=settings.HF_TOKEN,
            cache_dir=cache_dir,
            allow_patterns=[
                "*.json", "*.safetensors", "*.bin", "*.txt", 
                "*.model", "*.pt", "*.pth", "*.onnx"
            ],
            ignore_patterns=["*.md", "*.gitattributes", "*.git"],
        )
        
        elapsed = time.time() - start_time
        elapsed_str = str(timedelta(seconds=int(elapsed)))
        
        print()
        print("="*70)
        print("✅ DOWNLOAD COMPLETE!")
        print("="*70)
        print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Time taken: {elapsed_str}")
        print(f"📂 Model location: {local_dir}")
        print()
        print(f"🎉 {model_info['name']} is now ready to use!")
        print("   Update your .env file:")
        print(f"   MODEL_NAME={repo_id}")
        print()
        
        return True
        
    except KeyboardInterrupt:
        print()
        print("="*70)
        print("⏸️  DOWNLOAD PAUSED")
        print("="*70)
        print("💡 Progress has been saved!")
        print("   Run this script again to resume download.")
        print()
        return False
        
    except Exception as e:
        print()
        print("="*70)
        print("❌ DOWNLOAD FAILED")
        print("="*70)
        print(f"Error: {e}")
        print()
        print("💡 Troubleshooting:")
        print("   • Check internet connection")
        print("   • Verify HF token is valid")
        print("   • Verify repository exists: https://huggingface.co/" + repo_id)
        print("   • Try a different model (idm-vton, ootdiffusion, ladi-vton)")
        print("   • Run script again to resume")
        print()
        return False


def list_available_models():
    """List all available VTO models"""
    print("\n" + "="*70)
    print("📋 Available Virtual Try-On Models")
    print("="*70)
    print()
    
    for key, info in VTO_MODELS.items():
        rec = "⭐ RECOMMENDED" if info.get("recommended") else ""
        print(f"{key:15} | {info['name']:15} | {info['size']:10} | {rec}")
        print(f"              Repository: {info['repo_id']}")
        print(f"              {info['description']}")
        print()


if __name__ == "__main__":
    print()
    print("╔" + "═"*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + " "*15 + "VTO MODEL DOWNLOADER" + " "*30 + "║")
    print("║" + " "*68 + "║")
    print("╚" + "═"*68 + "╝")
    
    # List available models
    list_available_models()
    
    # Get user choice
    print()
    print("Which model would you like to download?")
    print("  1. idm-vton (Recommended)")
    print("  2. ootdiffusion")
    print("  3. ladi-vton")
    print()
    
    choice = input("Enter choice (1-3) or model key: ").strip().lower()
    
    model_map = {
        "1": "idm-vton",
        "2": "ootdiffusion",
        "3": "ladi-vton"
    }
    
    model_key = model_map.get(choice, choice)
    
    if model_key not in VTO_MODELS:
        print(f"❌ Invalid choice: {choice}")
        sys.exit(1)
    
    # Download
    success = download_vto_model(model_key)
    
    if success:
        print("✨ Setup complete!")
        sys.exit(0)
    else:
        print("⏸️  Download paused or failed.")
        print("   Run this script again to continue.")
        sys.exit(1)

