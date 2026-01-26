#!/usr/bin/env python3
"""
Quick test to verify port binding works
"""
import os
import socket
import sys

PORT = int(os.environ.get("PORT", 10000))
HOST = "0.0.0.0"

print(f"Testing port binding on {HOST}:{PORT}")

try:
    # Try to bind to the port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(1)
    print(f"✓ Successfully bound to {HOST}:{PORT}")
    sock.close()
    sys.exit(0)
except Exception as e:
    print(f"✗ Failed to bind: {e}")
    sys.exit(1)
