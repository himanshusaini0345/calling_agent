# Windows Installation Guide

This guide covers multiple ways to install and run the Voice Assistant Pipeline on Windows.

## 📋 Prerequisites

- **Windows 10/11** (64-bit)
- **Python 3.8+** ([Download here](https://www.python.org/downloads/))
  - ⚠️ **Important**: Check "Add Python to PATH" during installation!
- **4GB+ RAM** (8GB+ recommended for larger models)
- **Internet connection** (for downloading models and dependencies)

---

## 🚀 Quick Install Methods

### Method 1: Automated Setup (Recommended)

This is the easiest way to get started:

1. **Download** the project files
2. **Double-click** `setup.bat`
3. Follow the on-screen prompts
4. Done! The script will:
   - Install all dependencies
   - Download TTS models
   - Create configuration files

**To run the server:**
- Double-click `start_server.bat`

---

### Method 2: Manual Setup

If you prefer manual installation:

```batch
REM 1. Open Command Prompt in the project folder
cd path\to\voice-assistant-pipeline

REM 2. Install dependencies
pip install -r requirements.txt

REM 3. Create models folder
mkdir models

REM 4. Download a Piper model (example: English US)
REM Download from: https://github.com/rhasspy/piper/releases
REM Place .onnx and .onnx.json files in the models folder

REM 5. Create .env file
copy .env.example .env
notepad .env

REM Add your OpenAI API key to .env:
REM OPENAI_API_KEY=sk-proj-your-key-here

REM 6. Update server.py with your model path
notepad server.py
REM Change: "model_path": "./models/your-model.onnx"

REM 7. Run the server
python server.py
```

---

### Method 3: Standalone Executable (No Python Required)

Build a standalone .exe file that includes everything:

```batch
REM 1. Install PyInstaller
pip install pyinstaller

REM 2. Build the executable
build_exe.bat

REM 3. Find your executable in: dist\VoiceAssistantServer.exe
```

**Pros:**
- No Python installation needed for end users
- Single executable file
- Easier distribution

**Cons:**
- Large file size (~200-500 MB)
- Longer startup time
- Build process takes time

---

### Method 4: Professional Installer (Advanced)

Create a Windows installer (.exe) with:
- Installation wizard
- Start menu shortcuts
- Desktop icons
- Automatic dependency setup

**Requirements:**
- [Inno Setup](https://jrsoftware.org/isinfo.php) (free)

**Steps:**

1. **Download and install Inno Setup**

2. **Build the executable** (optional but recommended):
   ```batch
   build_exe.bat
   ```

3. **Compile the installer**:
   ```batch
   REM Right-click installer.iss and select "Compile"
   REM Or use command line:
   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
   ```

4. **Find installer** in `installer_output\VoiceAssistantPipeline_Setup.exe`

5. **Distribute** the installer to users

---

## 🔧 Configuration

### Setting up API Keys

Edit `.env` file:

```env
# Required for LLM
OPENAI_API_KEY=sk-proj-your-key-here

# Optional - for cloud providers
DEEPGRAM_API_KEY=your-deepgram-key
CARTESIA_API_KEY=your-cartesia-key
```

### Choosing Providers

Edit `server.py` and modify the configuration:

```python
# For fully local setup (no cloud APIs except OpenAI)
STT_CONFIG = {
    "provider": "local",
    "model_size": "base",
}

TTS_CONFIG = {
    "provider": "local",
    "model_path": "./models/en_US-lessac-medium.onnx",
}

# For cloud providers (faster, requires API keys)
STT_CONFIG = {
    "provider": "deepgram",
}

TTS_CONFIG = {
    "provider": "cartesia",
}
```

---

## 📥 Downloading Piper Models

### Method 1: During Setup
Run `setup.bat` and choose a language when prompted.

### Method 2: Manual Download

1. Visit [Piper Voices](https://huggingface.co/rhasspy/piper-voices/tree/main)

2. Choose a voice (e.g., `en/en_US/lessac/medium`)

3. Download both files:
   - `en_US-lessac-medium.onnx`
   - `en_US-lessac-medium.onnx.json`

4. Place in `models/` folder

5. Update `server.py`:
   ```python
   "model_path": "./models/en_US-lessac-medium.onnx"
   ```

### Recommended Models by Language

| Language | Model Path | Quality | Size |
|----------|-----------|---------|------|
| English (US) | `en/en_US/lessac/medium` | High | ~60MB |
| Spanish (ES) | `es/es_ES/davefx/medium` | High | ~60MB |
| French (FR) | `fr/fr_FR/upmc/medium` | High | ~60MB |
| German (DE) | `de/de_DE/thorsten/medium` | High | ~60MB |

---

## 🐛 Troubleshooting

### "Python is not recognized"
- Reinstall Python and check "Add Python to PATH"
- Or add Python manually to PATH:
  1. Search for "Environment Variables" in Windows
  2. Edit "Path" under System Variables
  3. Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python3X`

### "No module named 'websockets'"
- Run: `pip install -r requirements.txt`
- Or run: `setup.bat`

### "Failed to download model"
- Check internet connection
- Download manually from Hugging Face
- Use a VPN if Hugging Face is blocked

### Server won't start
- Check `.env` file has valid `OPENAI_API_KEY`
- Verify model path in `server.py` is correct
- Look for error messages in the console

### High CPU usage
- Use smaller models:
  - STT: `"model_size": "tiny"`
  - TTS: Use `low` quality models
- Close other applications
- Consider using cloud providers (Deepgram, Cartesia)

### Port 9000 already in use
Edit `server.py`:
```python
SERVER_CONFIG = {
    "port": 9001,  # Change to any available port
}
```

---

## 🎯 Running in Production

### As a Windows Service

Use [NSSM (Non-Sucking Service Manager)](https://nssm.cc/):

```batch
REM 1. Download NSSM
REM 2. Install service
nssm install VoiceAssistant "C:\Python3X\python.exe" "C:\path\to\server.py"

REM 3. Start service
nssm start VoiceAssistant
```

### Auto-start on Windows Boot

1. Press `Win+R`
2. Type: `shell:startup`
3. Create shortcut to `start_server.bat` in that folder

---

## 📦 Distribution Checklist

When distributing to other users:

- [ ] Include `.env.example` (not your actual .env!)
- [ ] Include `setup.bat` for easy setup
- [ ] Include `README.md` and `QUICKSTART.md`
- [ ] Include models folder (optional, can download during setup)
- [ ] If using exe: Include `dist\` folder
- [ ] If using installer: Just the `.exe` installer file

---

## 🔄 Updating

To update to a new version:

```batch
REM 1. Backup your .env and models folder
REM 2. Download new version
REM 3. Restore .env and models
REM 4. Update dependencies
pip install -r requirements.txt --upgrade
```

---

## 📞 Support

If you encounter issues:

1. Check the [README.md](README.md) for detailed documentation
2. Review [QUICKSTART.md](QUICKSTART.md) for setup steps
3. Look for error messages in the console
4. Check that all prerequisites are met

---

## 🎉 Success!

Once setup is complete, you should see:

```
==================================================
🎙️  Voice Assistant Server
==================================================
STT Provider: local
LLM Provider: openai (gpt-4o-mini)
TTS Provider: local
==================================================
🚀 Server running at ws://0.0.0.0:9000
==================================================
```

Your voice assistant is now ready to accept connections!
