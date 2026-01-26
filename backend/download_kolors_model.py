"""
Download Kolors Virtual Try-On Model
====================================
Downloads the Kolors model with progress tracking and resume capability.
Run this overnight - takes ~8-50 hours depending on internet speed.
"""

import os
import sys
import time
from datetime import datetime, timedelta

# Fix Windows encoding
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

def download_kolors():
    """Download Kolors model with progress tracking"""
    
    print("\n" + "="*70)
    print("📥 Kolors Virtual Try-On Model Downloader")
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
    model_name = "Kwai-Kolors/Kolors-Virtual-Try-On"
    cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
    
    print()
    print("📊 Download Information:")
    print(f"   Model: {model_name}")
    print(f"   Size: ~8-13 GB")
    print(f"   Cache: {cache_dir}")
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
        # Download with progress
        local_dir = snapshot_download(
            repo_id=model_name,
            resume_download=True,  # Resume if interrupted
            local_files_only=False,
            token=settings.HF_TOKEN,
            cache_dir=cache_dir,
            allow_patterns=["*.json", "*.safetensors", "*.bin", "*.txt", "*.model"],  # Only download needed files
            ignore_patterns=["*.md", "*.gitattributes"],  # Skip docs
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
        print("🎉 Kolors Virtual Try-On is now ready to use!")
        print("   Run: python run_with_real_images.py")
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
        print("💡 Try again:")
        print("   • Check internet connection")
        print("   • Verify HF token is valid")
        print("   • Run script again to resume")
        print()
        return False


def check_model_status():
    """Check if model is already downloaded"""
    from huggingface_hub import try_to_load_from_cache, list_repo_files
    from app.core.config import settings
    
    model_name = "Kwai-Kolors/Kolors-Virtual-Try-On"
    
    try:
        # Check some key files
        key_files = [
            "model_index.json",
            "unet/config.json",
            "text_encoder/config.json"
        ]
        
        all_exist = True
        for file in key_files:
            result = try_to_load_from_cache(
                repo_id=model_name,
                filename=file,
                cache_dir=os.path.expanduser("~/.cache/huggingface/hub")
            )
            if result is None:
                all_exist = False
                break
        
        if all_exist:
            print()
            print("✅ Kolors model is already downloaded!")
            print("   You can use it right away.")
            print()
            return True
        else:
            print()
            print("📊 Model Status: Not fully downloaded")
            print("   Some files are missing or partially downloaded.")
            print()
            return False
            
    except Exception as e:
        print()
        print("📊 Model Status: Not downloaded")
        print()
        return False


if __name__ == "__main__":
    print()
    print("╔" + "═"*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + " "*20 + "KOLORS MODEL DOWNLOADER" + " "*25 + "║")
    print("║" + " "*68 + "║")
    print("╚" + "═"*68 + "╝")
    
    # Check if already downloaded
    if check_model_status():
        print("✨ All set! Model is ready to use.")
        sys.exit(0)
    
    # Download
    success = download_kolors()
    
    if success:
        print("✨ Setup complete!")
        sys.exit(0)
    else:
        print("⏸️  Download paused or failed.")
        print("   Run this script again to continue.")
        sys.exit(1)

