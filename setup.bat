@echo off
REM Voice Assistant Pipeline Setup Script for Windows
REM This script helps you get started quickly on Windows

setlocal

echo ========================================
echo    Voice Assistant Pipeline Setup
echo ========================================
echo.

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Found Python %PYTHON_VERSION%
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
echo [OK] pip upgraded
echo.

REM Install dependencies
echo Installing Python dependencies...
echo This may take a few minutes...
python -m pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Create models directory
echo Creating models directory...
if not exist "models" mkdir models
echo [OK] Models directory created
echo.

REM TTS Model Setup
echo ========================================
echo    TTS Model Setup
echo ========================================
echo.
echo Would you like to download a Piper TTS model? (y/n)
set /p download_piper=

if /i "%download_piper%"=="y" (
    echo.
    echo Available languages:
    echo 1^) English ^(US^) - Medium quality ^(recommended^)
    echo 2^) Spanish ^(ES^) - Medium quality
    echo 3^) French ^(FR^) - Medium quality
    echo 4^) German ^(DE^) - Medium quality
    echo 5^) Skip ^(I'll download manually^)
    echo.
    set /p lang_choice=Enter choice (1-5): 
    
    set model_name=
    set model_url=
    set config_url=
    
    if "%lang_choice%"=="1" (
        set model_url=https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
        set config_url=https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
        set model_name=en_US-lessac-medium
    )
    if "%lang_choice%"=="2" (
        set model_url=https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx
        set config_url=https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx.json
        set model_name=es_ES-davefx-medium
    )
    if "%lang_choice%"=="3" (
        set model_url=https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/upmc/medium/fr_FR-upmc-medium.onnx
        set config_url=https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/upmc/medium/fr_FR-upmc-medium.onnx.json
        set model_name=fr_FR-upmc-medium
    )
    if "%lang_choice%"=="4" (
        set model_url=https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx
        set config_url=https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx.json
        set model_name=de_DE-thorsten-medium
    )
    
    if not "%model_name%"=="" (
        echo.
        echo Downloading %model_name%...
        echo This may take a few minutes depending on your connection...
        
        REM Try using curl (Windows 10+)
        curl --version >nul 2>&1
        if %errorlevel% equ 0 (
            echo Using curl to download...
            curl -L -o "models\%model_name%.onnx" "%model_url%" --progress-bar
            curl -L -o "models\%model_name%.onnx.json" "%config_url%" --progress-bar
        ) else (
            REM Fallback to PowerShell
            echo Using PowerShell to download...
            powershell -Command "Invoke-WebRequest -Uri '%model_url%' -OutFile 'models\%model_name%.onnx'"
            powershell -Command "Invoke-WebRequest -Uri '%config_url%' -OutFile 'models\%model_name%.onnx.json'"
        )
        
        if exist "models\%model_name%.onnx" (
            echo [OK] Model downloaded to models\%model_name%.onnx
            
            REM Update server.py with model path
            echo.
            echo Updating server.py with model path...
            set model_path=./models/%model_name%.onnx
            
            REM Use PowerShell to replace the path
            powershell -Command "(Get-Content server.py) -replace '\"model_path\": \"/path/to/piper/model.onnx\"', '\"model_path\": \"%model_path%\"' | Set-Content server.py"
            echo [OK] server.py updated
        ) else (
            echo [ERROR] Failed to download model
            echo You can download it manually from:
            echo %model_url%
        )
    ) else (
        echo [SKIP] Skipping model download
    )
)

echo.
echo ========================================
echo    API Keys Setup
echo ========================================
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env >nul
    echo [OK] .env file created
    echo.
    echo [WARNING] Please edit .env and add your OpenAI API key:
    echo    OPENAI_API_KEY=sk-proj-your-key-here
    echo.
    echo Optional API keys ^(for cloud providers^):
    echo    DEEPGRAM_API_KEY ^(for cloud STT^)
    echo    CARTESIA_API_KEY ^(for cloud TTS^)
    echo.
    echo Opening .env file for editing...
    timeout /t 2 >nul
    notepad .env
) else (
    echo [OK] .env file already exists
)

echo.
echo ========================================
echo    Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Make sure .env has your OPENAI_API_KEY
echo 2. ^(Optional^) Update server.py with your preferred provider settings
echo 3. Run: python server.py
echo.
echo For detailed instructions, see:
echo - QUICKSTART.md - Quick start guide
echo - README.md - Full documentation
echo - ARCHITECTURE.md - System architecture
echo.
echo Press any key to exit...
pause >nul