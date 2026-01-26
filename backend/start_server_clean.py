"""
Start Server with Clean Output
==============================
Suppresses harmless MediaPipe/TensorFlow warnings
"""
import os
import warnings
import sys

# Suppress specific warnings before imports
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow warnings
os.environ['GLOG_minloglevel'] = '3'  # Suppress MediaPipe warnings

# Filter warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', message='.*inference_feedback_manager.*')

if __name__ == "__main__":
    import uvicorn
    from app.core.config import settings
    
    print("\n" + "="*60)
    print("Starting Virtue Try-On Complete API")
    print("="*60)
    print(f"\nServer: http://{settings.HOST}:{settings.PORT}")
    print(f"API Docs: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"Environment: {'Development' if settings.DEBUG else 'Production'}")
    print("\nPress CTRL+C to stop\n")
    print("="*60 + "\n")
    
    # Run with clean output
    uvicorn.run(
        "complete_api:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
