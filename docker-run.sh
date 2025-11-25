#!/usr/bin/env bash

# ======================================================
# WeatherProject - Docker Launcher (Direct Mode)
# Replaces docker-compose to avoid version compatibility issues
# and fixes database persistence paths.
# ======================================================

set -e

echo "🐳 WeatherProject Docker Launcher"
echo "=================================="

# 1. Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ ERROR: Docker is not installed!"
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# 2. Check .env
if [ ! -f ".env" ]; then
    echo "❌ ERROR: .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi

# 3. Sudo Check
DOCKER_CMD="docker"
if ! docker ps &> /dev/null; then
    echo "⚠️  Docker requires sudo (user not in docker group)"
    echo "   Using sudo for docker commands..."
    DOCKER_CMD="sudo docker"
fi

# 4. Build
echo ""
echo "🔨 Building Docker image (weather-app)..."
$DOCKER_CMD build -t weather-app .

# 5. Cleanup Old Container
echo ""
echo "🧹 Cleaning up old container..."
$DOCKER_CMD rm -f weather-prediction-app 2>/dev/null || true

# 6. Run
echo ""
echo "🚀 Starting container..."
# Volume Mappings:
# - ./db:/app/db : Persist SQLite database (Fixes persistence bug)
# - ./logs:/app/logs : Access logs from host
$DOCKER_CMD run -d \
    --name weather-prediction-app \
    -p 8000:8000 \
    -p 8080:8080 \
    --env-file .env \
    -v "$(pwd)/db:/app/db" \
    -v "$(pwd)/logs:/app/logs" \
    --restart unless-stopped \
    weather-app > /dev/null

echo "✅ WeatherProject is running!"
echo "----------------------------------------"
echo "🔗 FastAPI Backend: http://localhost:8000"
echo "🔗 NiceGUI Frontend: http://localhost:8080"
echo "----------------------------------------"

# 7. Handle Shutdown
function cleanup {
    echo ""
    echo "🛑 Stopping container..."
    $DOCKER_CMD stop weather-prediction-app > /dev/null
    echo "✅ App stopped."
}

# Trap SIGINT (Ctrl+C) and EXIT
trap cleanup SIGINT EXIT

echo "📄 Following logs (Press CTRL+C to stop app)..."
echo ""
$DOCKER_CMD logs -f weather-prediction-app
