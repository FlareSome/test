# Multi-stage Dockerfile for Weather Prediction System
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data db

# Expose ports
# 8000 for FastAPI backend
# 8080 for NiceGUI frontend
EXPOSE 8000 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV API_BASE=http://localhost:8000

# Create startup script
RUN echo '#!/bin/bash\n\
    set -e\n\
    echo "🚀 Starting WeatherProject in Docker..."\n\
    \n\
    # Check for ML Model and Setup if missing\n\
    if [ ! -f "db/trained_weather_model.pkl" ]; then\n\
    echo "⚠️ ML Model not found! Running setup..."\n\
    python setup_ml.py\n\
    fi\n\
    \n\
    # Start Serial Reader in background\n\
    echo "📡 Starting serial reader..."\n\
    python serial/serial_reader.py > logs/serial.log 2>&1 &\n\
    SERIAL_PID=$!\n\
    \n\
    # Start FastAPI backend in background\n\
    echo "⚙️ Starting FastAPI backend..."\n\
    uvicorn main:app --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &\n\
    API_PID=$!\n\
    \n\
    # Start NiceGUI UI in foreground\n\
    echo "🌐 Starting NiceGUI UI..."\n\
    python ui/ui.py\n\
    ' > /app/docker-start.sh && chmod +x /app/docker-start.sh

# Run the startup script
CMD ["/app/docker-start.sh"]
