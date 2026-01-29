# Quick Start Guide

## 🚀 Get Started in 5 Minutes (Local Setup)

This guide will help you set up a **fully local** voice assistant that runs on CPU without requiring any API keys (except for OpenAI LLM).

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Download Piper Voice Model

Choose a voice from [Piper Voices](https://github.com/rhasspy/piper/releases/tag/v1.0.0):

```bash
# Create models directory
mkdir -p models

# Download English (US) voice - Medium quality
cd models
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
cd ..
```

**Other language options:**
- Spanish: `es/es_ES/davefx/medium/es_ES-davefx-medium.onnx`
- French: `fr/fr_FR/upmc/medium/fr_FR-upmc-medium.onnx`
- German: `de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx`
- [See all voices](https://github.com/rhasspy/piper/blob/master/VOICES.md)

### Step 3: Create .env File

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-proj-your-key-here
```

### Step 4: Configure Server

Edit `server.py` and update the TTS model path:

```python
TTS_CONFIG = {
    "provider": "local",
    "model_path": "./models/en_US-lessac-medium.onnx",  # ← Update this path
}
```

**Full local configuration:**

```python
STT_CONFIG = {
    "provider": "local",
    "model_size": "base",  # Good balance of speed/accuracy
    "language": None,  # Auto-detect language
    "device": "cpu",
    "compute_type": "int8",
}

LLM_CONFIG = {
    "provider": "openai",
    "model": "gpt-4o-mini",
}

TTS_CONFIG = {
    "provider": "local",
    "model_path": "./models/en_US-lessac-medium.onnx",
}
```

### Step 5: Run the Server

```bash
python server.py
```

You should see:

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

### Step 6: Test It

Send audio to `ws://localhost:9000` as 16-bit PCM at 16kHz (mono).

The server will:
1. ✅ Transcribe your speech (Faster Whisper)
2. ✅ Generate a response (OpenAI)
3. ✅ Synthesize speech (Piper)
4. ✅ Send audio back to you

---

## 🌐 Switching to Cloud Providers

### Use Deepgram for STT

1. Get API key from [Deepgram](https://deepgram.com)
2. Add to `.env`: `DEEPGRAM_API_KEY=your-key`
3. Update config:

```python
STT_CONFIG = {
    "provider": "deepgram",
    "model": "nova-2",
    "language": "en",
}
```

### Use Cartesia for TTS

1. Get API key from [Cartesia](https://cartesia.ai)
2. Add to `.env`: `CARTESIA_API_KEY=your-key`
3. Update config:

```python
TTS_CONFIG = {
    "provider": "cartesia",
    "voice_id": "a0e99841-438c-4a64-b679-ae501e7d6091",
}
```

---

## 🌍 Multilingual Support

### Spanish Example

```python
STT_CONFIG = {
    "provider": "local",
    "model_size": "base",
    "language": "es",  # Spanish
}

LLM_CONFIG = {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "system_prompt": "Eres un asistente útil. Responde de forma concisa.",
}

TTS_CONFIG = {
    "provider": "local",
    "model_path": "./models/es_ES-davefx-medium.onnx",  # Spanish voice
}
```

### Auto-detect Language

```python
STT_CONFIG = {
    "provider": "local",
    "language": None,  # Auto-detect!
}
```

Faster Whisper supports 99+ languages automatically.

---

## ⚡ Performance Tips

### Faster Response Time
- Use `"model_size": "tiny"` or `"base"` for STT
- Use `gpt-4o-mini` instead of `gpt-4o`
- Use cloud TTS (Cartesia) for lower latency

### Better Accuracy
- Use `"model_size": "small"` or `"medium"` for STT
- Use `gpt-4o` for more capable responses
- Specify exact language instead of auto-detect

### Low Resource Usage
- Use `"model_size": "tiny"` 
- Use `"compute_type": "int8"`
- Lower quality Piper voices (low/x_low)

---

## 🐛 Troubleshooting

### "faster-whisper" not found
```bash
pip install faster-whisper --upgrade
```

### "piper" not found
```bash
pip install piper-tts
```

### Model download is slow
- Models are cached in `~/.cache/huggingface/`
- First run downloads models (500MB-3GB depending on size)
- Subsequent runs are instant

### High CPU usage
- Use smaller models: `tiny` or `base`
- Reduce audio quality settings
- Add delays between processing chunks

---

## 📚 Next Steps

- Check `config_examples.py` for more configurations
- Read `README.md` for detailed documentation
- Implement your own providers (see "Adding New Providers")
- Integrate with your frontend application
