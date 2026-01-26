FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (with error handling)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    || echo "Warning: Some packages failed to install"

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for uploads and outputs
RUN mkdir -p static/uploads static/generated_outputs

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "complete_api:app", "--host", "0.0.0.0", "--port", "8000"]