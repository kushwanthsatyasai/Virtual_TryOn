#!/usr/bin/env python3
"""
Startup script for Render - ensures proper port binding
"""
import os
import sys

# Get port from environment (Render automatically sets this)
PORT = int(os.environ.get("PORT", 8000))
HOST = "0.0.0.0"

print(f"=" * 60)
print(f"Starting Virtue Try-On API")
print(f"Host: {HOST}")
print(f"Port: {PORT}")
print(f"PORT env var: {os.environ.get('PORT', 'NOT SET')}")
print(f"=" * 60)
sys.stdout.flush()

try:
    # Import uvicorn first
    import uvicorn
    print("✓ uvicorn imported")
    sys.stdout.flush()
    
    # Import the app
    print("Importing complete_api...")
    sys.stdout.flush()
    from complete_api import app
    print("✓ complete_api imported")
    sys.stdout.flush()
    
    # Start the server
    print(f"Starting server on {HOST}:{PORT}...")
    sys.stdout.flush()
    
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        workers=1,
        log_level="info",
        access_log=True
    )
    
except ImportError as e:
    print(f"❌ IMPORT ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.stdout.flush()
    sys.exit(1)
    
except Exception as e:
    print(f"❌ STARTUP ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.stdout.flush()
    sys.exit(1)
