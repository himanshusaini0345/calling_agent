# Building Windows Executables & Installers

This guide explains how to build and distribute the Voice Assistant Pipeline for Windows users.

## 🎯 Distribution Options

### Option 1: Python Scripts (Simplest)
**Pros:** Small size, easy updates
**Cons:** Requires Python installation
**Best for:** Developers, technical users

### Option 2: Standalone Executable
**Pros:** No Python needed, single file
**Cons:** Large size (~200-500MB)
**Best for:** Non-technical users, demos

### Option 3: Windows Installer
**Pros:** Professional, includes shortcuts, guided setup
**Cons:** Most complex to build
**Best for:** Production distribution, end users

---

## 📦 Option 1: Python Scripts Distribution

### What to Include

```
voice-assistant-pipeline.zip
├── server.py
├── pipeline.py
├── config_examples.py
├── test_client.py
├── requirements.txt
├── setup.bat
├── start_server.bat
├── .env.example
├── LICENSE.txt
├── README.md
├── QUICKSTART.md
├── WINDOWS_INSTALL.md
└── providers/
    ├── __init__.py
    ├── base.py
    ├── factory.py
    ├── stt_local.py
    ├── stt_deepgram.py
    ├── llm_openai.py
    ├── tts_local.py
    └── tts_cartesia.py
```

### Build Steps

```batch
REM 1. Create clean directory
mkdir dist-python
cd dist-python

REM 2. Copy all files
xcopy /E /I ..\*.py .
xcopy /E /I ..\*.bat .
xcopy /E /I ..\*.txt .
xcopy /E /I ..\*.md .
xcopy /E /I ..\providers providers

REM 3. Create zip
powershell Compress-Archive -Path * -DestinationPath ..\VoiceAssistant-Python.zip

REM 4. Distribute VoiceAssistant-Python.zip
```

### User Instructions

Users need to:
1. Install Python 3.8+
2. Extract zip
3. Run `setup.bat`
4. Edit `.env` with API key
5. Run `start_server.bat`

---

## 🚀 Option 2: Standalone Executable

### Prerequisites

```batch
pip install pyinstaller
```

### Build Process

#### Step 1: Test the Spec File

The `voice_assistant.spec` file is already configured. Review it:

```python
# Key settings in voice_assistant.spec:
- name='VoiceAssistantServer'  # Output exe name
- console=True                 # Shows console for logs
- hiddenimports=[...]          # All required modules
```

#### Step 2: Build the Executable

```batch
REM Clean build (recommended)
pyinstaller voice_assistant.spec --clean --noconfirm

REM Or use the provided script
build_exe.bat
```

This creates:
```
dist/
└── VoiceAssistantServer.exe  (~200-500MB)
```

#### Step 3: Create Distribution Package

The exe alone isn't enough! Users need:

```
VoiceAssistant-Standalone/
├── VoiceAssistantServer.exe   (main executable)
├── .env.example               (API key template)
├── README_WINDOWS.txt         (user instructions)
├── LICENSE.txt
└── models/                    (empty folder for TTS models)
```

Build script:

```batch
REM Create distribution folder
mkdir VoiceAssistant-Standalone
cd VoiceAssistant-Standalone

REM Copy executable
copy ..\dist\VoiceAssistantServer.exe .

REM Copy support files
copy ..\.env.example .
copy ..\README_WINDOWS.txt README.txt
copy ..\LICENSE.txt .

REM Create models folder
mkdir models

REM Create instruction file
echo Please edit .env file and add your OpenAI API key > INSTRUCTIONS.txt
echo Download Piper models to the models folder >> INSTRUCTIONS.txt

REM Zip it
cd ..
powershell Compress-Archive -Path VoiceAssistant-Standalone -DestinationPath VoiceAssistant-Standalone.zip
```

### Size Optimization

To reduce exe size:

```python
# In voice_assistant.spec, add excludes:
excludes=['matplotlib', 'IPython', 'jupyter', 'scipy'],

# Use UPX compression (if available)
upx=True,
upx_exclude=[],
```

**Note:** Even optimized, exe will be 150-300MB due to:
- Python runtime
- NumPy/ML libraries
- Faster Whisper models

---

## 🎨 Option 3: Professional Windows Installer

### Prerequisites

1. **Download Inno Setup** (free)
   - [https://jrsoftware.org/isinfo.php](https://jrsoftware.org/isinfo.php)
   - Install with default options

2. **Build executable first** (optional but recommended)
   ```batch
   build_exe.bat
   ```

### Customize Installer

Edit `installer.iss`:

```pascal
; Update these values
#define MyAppName "Voice Assistant Pipeline"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Your Name or Company"
#define MyAppURL "https://your-website.com"

; Generate unique GUID at: https://www.guidgenerator.com/
AppId={{YOUR-GUID-HERE}}
```

### Add Custom Icon (Optional)

```pascal
; Create a 256x256 .ico file
SetupIconFile=icon.ico
```

Create `icon.ico`:
- Use online tools like [ICO Converter](https://convertio.co/png-ico/)
- Or use GIMP, Photoshop, etc.

### Build the Installer

**Method 1: GUI**
1. Right-click `installer.iss`
2. Select "Compile"
3. Wait for build to complete

**Method 2: Command Line**
```batch
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

Output:
```
installer_output/
└── VoiceAssistantPipeline_Setup.exe  (~200-500MB if includes exe)
```

### What the Installer Does

1. **Welcome Screen** - Shows app info
2. **Python Check** - Warns if Python not installed
3. **License Agreement** - Shows LICENSE.txt
4. **Choose Location** - Default: Program Files
5. **Select Components** - Choose what to install
6. **Create Shortcuts** - Desktop, Start Menu
7. **Install Files** - Copies all files
8. **Run Setup** - Optionally runs setup.bat
9. **Finish** - Shows quick start guide

### Installer Features

✅ **Automatic:**
- Creates Start Menu shortcuts
- Creates desktop icon (optional)
- Sets up file structure
- Checks for Python

✅ **User-Friendly:**
- Multi-language support
- Progress bar
- Guided setup
- Professional appearance

✅ **Smart:**
- Detects Python installation
- Offers to run setup.bat
- Creates uninstaller

---

## 📋 Pre-Distribution Checklist

Before distributing, ensure:

### Code Quality
- [ ] All imports work
- [ ] No hardcoded paths (use relative paths)
- [ ] No personal API keys in code
- [ ] Error handling is robust
- [ ] Logging is informative

### Testing
- [ ] Test on clean Windows machine
- [ ] Test without Python (if using exe)
- [ ] Test with fresh .env file
- [ ] Test model download process
- [ ] Verify all providers work

### Documentation
- [ ] README is clear and complete
- [ ] QUICKSTART guide is accurate
- [ ] WINDOWS_INSTALL has all steps
- [ ] API key instructions are clear
- [ ] Troubleshooting section is helpful

### Files
- [ ] No .pyc files included
- [ ] No __pycache__ folders
- [ ] No personal .env file
- [ ] LICENSE.txt included
- [ ] Version numbers are correct

### Legal
- [ ] License is appropriate
- [ ] Third-party licenses acknowledged
- [ ] No proprietary code included

---

## 🚢 Distribution Methods

### Method 1: Direct Download
- Upload to your website
- Share via Google Drive, Dropbox
- Host on GitHub Releases

### Method 2: GitHub Release
```bash
# Create a release
git tag v1.0.0
git push origin v1.0.0

# Upload artifacts:
- VoiceAssistant-Python.zip
- VoiceAssistant-Standalone.zip
- VoiceAssistantPipeline_Setup.exe
```

### Method 3: Microsoft Store (Advanced)
- Requires developer account ($19 one-time)
- Must package as MSIX
- Full documentation: [docs.microsoft.com](https://docs.microsoft.com/en-us/windows/apps/publish/)

---

## 📊 Size Comparison

| Method | Size | Requires Python |
|--------|------|----------------|
| Python Scripts | ~50KB | Yes |
| + Dependencies | ~500MB* | Yes |
| Standalone Exe | 200-500MB | No |
| Installer | 250-550MB | No** |

\* Downloaded on first run via pip
\** Can optionally check and use existing Python installation

---

## 🔄 Version Updates

### For Python Distribution
1. Update version in README.md
2. Update CHANGELOG (create if needed)
3. Re-zip and distribute

### For Executable
1. Update version in `voice_assistant.spec`
2. Rebuild: `build_exe.bat`
3. Test thoroughly
4. Redistribute

### For Installer
1. Update `#define MyAppVersion` in `installer.iss`
2. Update CHANGELOG
3. Rebuild installer
4. Test on clean machine
5. Distribute

---

## 🐛 Common Build Issues

### PyInstaller Fails
```
Error: Module not found
Solution: Add to hiddenimports in .spec file
```

### Executable Too Large
```
Problem: 800MB+ exe
Solution: Exclude unused packages, enable UPX compression
```

### Exe Crashes on Start
```
Problem: Missing dependencies
Solution: Check hiddenimports, test on clean machine
```

### Models Not Found
```
Problem: Hardcoded paths
Solution: Use relative paths: ./models/
```

---

## 📝 Notes

- **Antivirus**: Standalone exes may trigger false positives. Submit to antivirus vendors for whitelisting.
- **Code Signing**: For professional distribution, get a code signing certificate (~$100-500/year)
- **Auto-updates**: Consider implementing update checking in your app
- **Telemetry**: Optional, but helps track issues and usage

---

## ✅ Final Checklist Before Release

- [ ] Tested on Windows 10 and 11
- [ ] Tested on clean machine without Python
- [ ] All documentation is accurate
- [ ] Version numbers are consistent
- [ ] No API keys or secrets included
- [ ] License file included
- [ ] README is clear for non-developers
- [ ] Installer (if used) installs correctly
- [ ] Uninstaller works properly
- [ ] All features work as expected
- [ ] Error messages are helpful
- [ ] Support/contact info provided

---

Happy building! 🎉
