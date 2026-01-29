# Voice Assistant Pipeline - Windows Executable

## Quick Start for Non-Developers

This folder contains a ready-to-run voice assistant server.

### What You Need

1. **Windows 10/11** (64-bit)
2. **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))
3. **4GB+ RAM**

### Installation Steps

#### Option 1: Python Installation (Recommended)

1. **Install Python 3.8+**
   - Download from [python.org](https://www.python.org/downloads/)
   - ⚠️ **Important**: Check "Add Python to PATH" during install!

2. **Run Setup**
   - Double-click `setup.bat`
   - Follow the prompts to download voice models
   - Wait for dependencies to install

3. **Configure API Key**
   - Open `.env` file with Notepad
   - Replace `your-key-here` with your actual OpenAI API key:
     ```
     OPENAI_API_KEY=sk-proj-abc123xyz...
     ```
   - Save and close

4. **Start Server**
   - Double-click `start_server.bat`
   - You should see "Server running at ws://0.0.0.0:9000"

#### Option 2: Standalone Executable (If Available)

If `VoiceAssistantServer.exe` is included:

1. **Extract All Files**
   - Extract the entire folder (not just the .exe)

2. **Configure API Key**
   - Open `.env` file with Notepad
   - Add your OpenAI API key
   - Save and close

3. **Download Models**
   - Models must be downloaded separately
   - Run `setup.bat` or download from [Piper Voices](https://huggingface.co/rhasspy/piper-voices)
   - Place `.onnx` files in `models/` folder

4. **Run**
   - Double-click `VoiceAssistantServer.exe`

### Folder Structure

```
voice-assistant-pipeline/
├── VoiceAssistantServer.exe  (if using executable)
├── server.py                  (main server script)
├── setup.bat                  (setup wizard)
├── start_server.bat           (server launcher)
├── .env                       (your API keys - create from .env.example)
├── models/                    (TTS voice models - downloaded during setup)
├── providers/                 (provider implementations)
└── Documentation files
```

### Using the Voice Assistant

Once the server is running:

1. Connect your client app to `ws://localhost:9000`
2. Send audio (16-bit PCM, 16kHz, mono)
3. Receive AI-generated voice responses

See `QUICKSTART.md` for detailed usage instructions.

### Configuration

To customize providers, edit `server.py`:

**Use Local Providers** (no additional API keys needed):
```python
STT_CONFIG = {"provider": "local"}
TTS_CONFIG = {"provider": "local", "model_path": "./models/your-model.onnx"}
```

**Use Cloud Providers** (faster, requires API keys):
```python
STT_CONFIG = {"provider": "deepgram"}  # Requires DEEPGRAM_API_KEY
TTS_CONFIG = {"provider": "cartesia"}  # Requires CARTESIA_API_KEY
```

### Troubleshooting

**"Python is not recognized"**
- Reinstall Python with "Add to PATH" checked
- Restart your computer

**"Module not found"**
- Run `setup.bat` to install dependencies
- Or manually: `pip install -r requirements.txt`

**Server won't start**
- Check `.env` has valid `OPENAI_API_KEY`
- Verify model path in `server.py` is correct
- Ensure port 9000 is not in use

**High CPU usage**
- Use smaller models: edit `server.py` to use `"model_size": "tiny"`
- Close unnecessary applications
- Consider upgrading to cloud providers

### Getting Help

- Read `WINDOWS_INSTALL.md` for detailed installation guide
- Check `README.md` for full documentation
- Review `QUICKSTART.md` for quick start guide
- See `ARCHITECTURE.md` for technical details

### Languages Supported

The local STT (speech-to-text) supports 99+ languages automatically!

Common languages:
- English, Spanish, French, German, Italian
- Portuguese, Russian, Japanese, Chinese, Korean
- Arabic, Hindi, Dutch, and many more

Change TTS voice by downloading different Piper models.

### System Requirements

**Minimum:**
- Windows 10 (64-bit)
- 4GB RAM
- 2GB free disk space
- Internet connection (for setup)

**Recommended:**
- Windows 11
- 8GB+ RAM
- SSD for better performance
- Stable internet connection

### What's Included

✅ Modular provider system
✅ Local STT (Faster Whisper)
✅ Local TTS (Piper)
✅ Cloud provider support (Deepgram, Cartesia)
✅ OpenAI LLM integration
✅ WebSocket server
✅ Complete documentation
✅ Setup automation

### Privacy & Data

- **Local providers**: All processing happens on your computer
- **Cloud providers**: Audio/text sent to respective APIs
- **OpenAI**: Prompts sent to OpenAI API
- **No data storage**: This server doesn't store conversations

### License

This software is provided under the MIT License. See LICENSE.txt for details.

### Version

Version: 1.0.0
Last Updated: 2025

---

**Need More Help?**

Check the documentation files or contact the developer.

Enjoy your voice assistant! 🎙️
