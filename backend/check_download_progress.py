"""
Check Kolors Model Download Progress
====================================
Run this while downloading to check how much is downloaded.
"""

import os
import sys
from pathlib import Path

if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

def get_folder_size(path):
    """Get total size of folder in bytes"""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_folder_size(entry.path)
    except Exception:
        pass
    return total

def format_size(bytes):
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"

def check_progress():
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    
    print()
    print("="*70)
    print("📊 Kolors Model Download Progress")
    print("="*70)
    print()
    
    # Find Kolors model folders
    kolors_folders = []
    if cache_dir.exists():
        for folder in cache_dir.iterdir():
            if "kolors" in folder.name.lower():
                kolors_folders.append(folder)
    
    if not kolors_folders:
        print("❌ No Kolors model found in cache")
        print(f"   Cache location: {cache_dir}")
        print()
        print("💡 Model hasn't started downloading yet")
        print("   Run: python download_kolors_model.py")
        print()
        return
    
    # Calculate sizes
    total_size = 0
    for folder in kolors_folders:
        size = get_folder_size(folder)
        total_size += size
        print(f"📁 {folder.name}")
        print(f"   Size: {format_size(size)}")
        print()
    
    print("="*70)
    print(f"📦 Total Downloaded: {format_size(total_size)}")
    print(f"🎯 Target Size: ~8-13 GB")
    
    # Estimate progress
    target_gb = 10.5  # Average
    current_gb = total_size / (1024**3)
    progress_pct = min(100, (current_gb / target_gb) * 100)
    
    print(f"📈 Progress: ~{progress_pct:.1f}%")
    print()
    
    if progress_pct >= 95:
        print("✅ Download appears complete!")
        print("   Try running: python run_with_real_images.py")
    elif progress_pct > 0:
        print("⏳ Download in progress...")
        print("   Keep laptop on and connected to internet")
    else:
        print("🚀 Download starting...")
    
    print("="*70)
    print()

if __name__ == "__main__":
    try:
        check_progress()
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")

