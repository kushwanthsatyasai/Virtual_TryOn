#!/bin/bash
# Build script for Render deployment
# Installs system dependencies needed for Python packages

set -e  # Exit on error

echo "Installing system dependencies..."

# Update package list
apt-get update -qq

# Install minimal system dependencies
apt-get install -y -qq \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    gcc \
    g++ \
    || echo "Some packages failed to install, continuing..."

# Clean up
apt-get clean
rm -rf /var/lib/apt/lists/*

echo "System dependencies installed."

# Install Python packages
pip install --no-cache-dir -r requirements.txt

echo "Build complete!"
