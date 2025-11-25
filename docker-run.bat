@echo off
REM ======================================================
REM WeatherProject - Docker Launcher (Windows)
REM ======================================================

echo.
echo 🐳 WeatherProject Docker Launcher
echo ==================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Docker is not installed!
    echo.
    echo Please install Docker Desktop from: https://docs.docker.com/desktop/install/windows-install/
    echo.
    echo IMPORTANT: Make sure to enable WSL2 backend for best performance
    pause
    exit /b 1
)

REM Check if Docker Desktop is running
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Docker Desktop is not running!
    echo.
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo ❌ ERROR: .env file not found!
    echo.
    echo Please create a .env file with your configuration:
    echo   1. Copy .env.example to .env
    echo   2. Edit .env with your API keys
    echo.
    echo Example:
    echo   copy .env.example .env
    echo.
    pause
    exit /b 1
)

echo ✅ Docker Desktop is running
echo ✅ .env file found
echo.

REM Build and run with docker-compose
echo 🔨 Building Docker image...
docker compose build
if %errorlevel% neq 0 (
    echo.
    echo ❌ Build failed! Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo 🚀 Starting containers...
echo.
echo ----------------------------------------
echo 🔗 FastAPI Backend: http://localhost:8000
echo 🔗 NiceGUI Frontend: http://localhost:8080
echo ----------------------------------------
echo.
echo Press Ctrl+C to stop the containers
echo.

docker compose up
