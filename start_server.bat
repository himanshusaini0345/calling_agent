@echo off
REM Voice Assistant Server Launcher for Windows
REM This script starts the voice assistant server

setlocal

echo ========================================
echo    Voice Assistant Server
echo ========================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo Please run setup.bat first
    echo.
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if dependencies are installed
python -c "import websockets" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Dependencies not installed
    echo Please run setup.bat first
    echo.
    pause
    exit /b 1
)

echo Starting Voice Assistant Server...
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python server.py

pause
