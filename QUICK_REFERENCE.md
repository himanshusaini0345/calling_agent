# ⚡ Quick Reference Card

## 🎯 3 Steps to Get Started

### Windows Users (Easiest Way)
```
┌─────────────────────────────────────┐
│  1. Double-click: setup.bat         │
│  2. Edit .env (add API key)         │
│  3. Double-click: start_server.bat  │
└─────────────────────────────────────┘
```

### Linux/Mac Users
```bash
bash setup.sh && python server.py
```

---

## 📁 Which Files Do I Need?

### 🟢 Essential Files (Must Have)
```
✓ server.py              - Main server
✓ pipeline.py            - Pipeline logic
✓ providers/             - Provider modules
✓ requirements.txt       - Dependencies
✓ .env                   - Your API keys
```

### 🟡 Setup Files (Makes Life Easy)
```
✓ setup.bat             - Windows setup
✓ setup.sh              - Linux/Mac setup
✓ start_server.bat      - Windows launcher
```

### 🔵 Documentation (Helpful)
```
✓ README.md             - Full docs
✓ QUICKSTART.md         - Fast start
✓ WINDOWS_INSTALL.md    - Windows guide
```

### 🟣 Distribution Files (For Sharing)
```
○ build_exe.bat          - Build executable
○ voice_assistant.spec   - PyInstaller config
○ installer.iss          - Installer script
```

---

## 🔑 API Keys Needed

### Required
- **OpenAI API Key** - For the AI brain
  - Get it: https://platform.openai.com/api-keys
  - Cost: ~$0.01 per conversation

### Optional (Only for Cloud Providers)
- **Deepgram** - For cloud speech-to-text
- **Cartesia** - For cloud text-to-speech

---

## ⚙️ Configuration Presets

Copy these into `server.py`:

### 🏠 Local Setup (Privacy, No Extra APIs)
```python
STT_CONFIG = {"provider": "local", "model_size": "base"}
TTS_CONFIG = {"provider": "local", "model_path": "./models/en_US.onnx"}
```

### ☁️ Cloud Setup (Speed, Requires APIs)
```python
STT_CONFIG = {"provider": "deepgram"}
TTS_CONFIG = {"provider": "cartesia"}
```

### ⚖️ Hybrid Setup (Balance)
```python
STT_CONFIG = {"provider": "local"}
TTS_CONFIG = {"provider": "cartesia"}
```

---

## 🌍 Language Support

### Change STT Language
```python
STT_CONFIG = {
    "language": "es"  # Spanish
    # Or: "en", "fr", "de", "it", "pt", "ru", "ja", "zh", "ko", "ar"
    # Or: None  (auto-detect)
}
```

### Change TTS Voice
1. Download voice from: https://huggingface.co/rhasspy/piper-voices
2. Update path:
```python
TTS_CONFIG = {
    "model_path": "./models/es_ES-voice.onnx"  # Spanish
}
```

---

## 🚨 Troubleshooting

### ❌ "Python not found"
```
Solution: Install Python 3.8+
Download: https://www.python.org/downloads/
Check: "Add Python to PATH" during install
```

### ❌ "Module not found"
```
Solution: Run setup script
Windows: setup.bat
Linux:   bash setup.sh
```

### ❌ "API key invalid"
```
Solution: Check .env file
Format:  OPENAI_API_KEY=sk-proj-abc123...
No quotes, no spaces around =
```

### ❌ Server won't start
```
Checklist:
✓ .env file exists?
✓ API key is valid?
✓ Model path correct?
✓ Port 9000 available?
```

### ❌ High CPU usage
```
Solutions:
1. Use smaller model: "model_size": "tiny"
2. Use cloud providers
3. Close other apps
```

---

## 📊 Performance Comparison

| Setup | Speed | Privacy | Cost | Setup Time |
|-------|-------|---------|------|------------|
| All Local | Medium | ★★★★★ | Low | 10 min |
| All Cloud | Fast | ★★☆☆☆ | Medium | 5 min |
| Hybrid | Fast | ★★★★☆ | Medium | 8 min |

---

## 🎓 Learning Path

### Beginner
1. Read `QUICKSTART.md`
2. Run `setup.bat`
3. Start server
4. Connect client

### Intermediate
1. Try different providers
2. Test multiple languages
3. Optimize performance
4. Read `ARCHITECTURE.md`

### Advanced
1. Add custom providers
2. Build executable
3. Create installer
4. Read `BUILD_GUIDE.md`

---

## 📞 Need Help?

### In Order of Helpfulness:

1. **Check error message** - Usually tells you what's wrong
2. **Read QUICKSTART.md** - Covers 90% of issues
3. **Check WINDOWS_INSTALL.md** - Windows-specific help
4. **Review troubleshooting** - Common issues & solutions
5. **Read full README.md** - Comprehensive documentation

---

## ✅ Success Checklist

You know it's working when:

- [ ] Server prints "Server running at ws://..."
- [ ] No error messages appear
- [ ] You can connect on port 9000
- [ ] Audio gets transcribed correctly
- [ ] AI responses make sense
- [ ] You hear synthesized speech

---

## 🎯 Common Tasks

### Change Port
```python
SERVER_CONFIG = {"port": 9001}  # Use any available port
```

### Change LLM Model
```python
LLM_CONFIG = {"model": "gpt-4o"}  # More capable, slower
```

### Disable Timing Logs
```python
PIPELINE_CONFIG = {"enable_timing": False}
```

### Speed Up Response
```python
STT_CONFIG = {"model_size": "tiny"}  # Fastest
LLM_CONFIG = {"model": "gpt-4o-mini"}  # Fastest GPT
TTS_CONFIG = {"provider": "cartesia"}  # Cloud = faster
```

---

## 💾 File Sizes

| File/Folder | Size |
|-------------|------|
| Python Scripts | ~100 KB |
| Dependencies | ~500 MB |
| STT Model (base) | ~150 MB |
| TTS Model | ~60 MB |
| **Total** | **~710 MB** |

*Executable: 200-500 MB (includes everything)*

---

## 🎨 Customization Ideas

- [ ] Add conversation history
- [ ] Implement wake word detection
- [ ] Create web UI
- [ ] Add user authentication
- [ ] Store conversation logs
- [ ] Add emotion detection
- [ ] Multi-user support
- [ ] Custom voice cloning

---

## 📱 Client Connection

```javascript
// JavaScript example
const ws = new WebSocket('ws://localhost:9000');

// Send audio (16-bit PCM, 16kHz, mono)
ws.send(audioBuffer);

// Receive response
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  const audio = base64Decode(data.data);
  playAudio(audio);
};
```

---

## 🔐 Security Notes

- **Never commit .env** to version control
- **Use environment variables** in production
- **Rotate API keys** regularly
- **Monitor API usage** to prevent abuse
- **Use HTTPS** for production (wss://)

---

## 📈 Scaling Up

### Single Machine
- Run as service
- Use process manager (PM2, systemd)
- Monitor with logging

### Multiple Machines
- Add load balancer
- Share state with Redis
- Use cloud deployment

### Production Ready
- Add authentication
- Implement rate limiting
- Set up monitoring
- Use container orchestration

---

## 🎉 You're Ready!

If you've read this far, you have everything you need to:

✅ Install the voice assistant
✅ Configure it for your needs
✅ Troubleshoot common issues
✅ Customize and extend it
✅ Deploy it to production

**Happy building!** 🚀

---

*Version 1.0.0 | Last updated: January 2025*
