FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY age_detector/ ./age_detector/
COPY download_models.py .
COPY models/ ./models/

# Download model if not present
RUN python download_models.py || true

# Expose port
EXPOSE 5000

# Run the API server
CMD ["python", "-m", "age_detector.api", "--host", "0.0.0.0", "--port", "5000"]
