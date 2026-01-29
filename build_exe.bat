@echo off
REM Build Windows executable using PyInstaller
REM This creates a standalone .exe file

setlocal

echo ========================================
echo    Building Windows Executable
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed
    pause
    exit /b 1
)

REM Install PyInstaller if not present
echo Checking for PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
    echo [OK] PyInstaller installed
) else (
    echo [OK] PyInstaller found
)

echo.
echo Installing dependencies...
python -m pip install -r requirements.txt --quiet
echo [OK] Dependencies installed

echo.
echo Building executable...
echo This may take several minutes...
echo.

pyinstaller voice_assistant.spec --clean --noconfirm

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo    Build Successful!
    echo ========================================
    echo.
    echo Executable created at: dist\VoiceAssistantServer.exe
    echo.
    echo To distribute:
    echo 1. Copy the entire dist folder
    echo 2. Include your .env file
    echo 3. Include the models folder with TTS models
    echo.
    echo Note: The executable is quite large because it includes
    echo all Python dependencies. For smaller distribution,
    echo consider using the Python scripts directly.
    echo.
) else (
    echo.
    echo [ERROR] Build failed
    echo Check the output above for errors
    echo.
)

pause
