#!/usr/bin/env python3
"""
Startup script for Render - ensures proper port binding
"""
import os
import sys

# Suppress ONNX Runtime GPU discovery warning on headless servers (no GPU)
os.environ.setdefault("ORT_LOG_LEVEL", "4")

# Get port from environment (Render automatically sets this)
# Handle empty string case (if PORT is set but empty)
port_str = os.environ.get("PORT", "")
if port_str and port_str.strip():
    PORT = int(port_str.strip())
else:
    PORT = 8000  # Default fallback
HOST = "0.0.0.0"

print(f"=" * 60)
print(f"Starting Virtue Try-On API")
print(f"Host: {HOST}")
print(f"Port: {PORT}")
port_env = os.environ.get('PORT', 'NOT SET')
print(f"PORT env var: {port_env} (using: {PORT})")
print(f"=" * 60)
sys.stdout.flush()

try:
    # Import uvicorn first
    import uvicorn
    print("✓ uvicorn imported")
    sys.stdout.flush()
    
    # Import the app with detailed error handling
    print("Importing complete_api...")
    sys.stdout.flush()
    try:
        from complete_api import app
        print("✓ complete_api imported")
        sys.stdout.flush()
        
        # Verify app is valid
        if app is None:
            raise ValueError("App is None after import")
        print(f"✓ App instance created: {type(app)}")
        sys.stdout.flush()
        
    except Exception as import_error:
        print(f"❌ ERROR importing app: {import_error}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        raise
    
    # Start the server - use uvicorn.run with explicit binding
    print(f"Starting server on {HOST}:{PORT}...")
    print(f"App ready, binding to port {PORT}...")
    print(f"PORT environment variable: {os.environ.get('PORT', 'NOT SET')}")
    sys.stdout.flush()
    
    # CRITICAL: Use uvicorn.run() which properly binds to the port
    # This must complete and stay running for Render to detect the port
    print("=" * 60)
    print("CALLING uvicorn.run() - Server should bind now")
    print("=" * 60)
    sys.stdout.flush()
    
    try:
        uvicorn.run(
            app,
            host=HOST,
            port=PORT,
            workers=1,
            log_level="info",
            access_log=True,
            loop="asyncio"
        )
    except Exception as run_error:
        print(f"❌ ERROR in uvicorn.run(): {run_error}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        sys.exit(1)
    
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
