# Modular Voice Assistant Pipeline

A flexible, modular voice assistant server with pluggable STT, LLM, and TTS providers. Supports both cloud and local (CPU-based) providers.

## Architecture

```
Audio Input → STT → LLM → TTS → Audio Output
              ↓     ↓     ↓
         [Provider Interfaces]
              ↓     ↓     ↓
    [Multiple Implementations]
```

### Components

- **STT (Speech-to-Text)**
  - Local: Faster Whisper (CPU, multilingual)
  - Cloud: Deepgram
  
- **LLM (Language Model)**
  - OpenAI (gpt-4o-mini, gpt-4o)
  
- **TTS (Text-to-Speech)**
  - Local: Piper (CPU)
  - Cloud: Cartesia

## Installation

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Download local models (if using local providers)

#### Faster Whisper (STT)
Models download automatically on first use. Supported sizes:
- `tiny` - Fastest, least accurate
- `base` - Good balance (recommended)
- `small` - Better accuracy
- `medium` - High accuracy
- `large-v3` - Best accuracy

#### Piper (TTS)
Download a voice model from [Piper voices](https://github.com/rhasspy/piper/releases/tag/v1.0.0):

```bash
# Example: Download English US voice
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
```

Update `TTS_CONFIG["model_path"]` in `server.py` with the path to your `.onnx` file.

### 3. Configure environment variables

Create a `.env` file:

```env
# Only needed if using cloud providers
OPENAI_API_KEY=your_openai_key
DEEPGRAM_API_KEY=your_deepgram_key
CARTESIA_API_KEY=your_cartesia_key
```

## Configuration

Edit `server.py` to switch providers:

### Use Local STT + Local TTS (No API keys needed!)

```python
STT_CONFIG = {
    "provider": "local",
    "model_size": "base",  # tiny, base, small, medium, large-v3
    "language": None,  # Auto-detect or specify: "en", "es", "fr", etc.
    "device": "cpu",
    "compute_type": "int8",
}

TTS_CONFIG = {
    "provider": "local",
    "model_path": "/path/to/your/piper-model.onnx",
}
```

### Use Cloud Providers

```python
STT_CONFIG = {
    "provider": "deepgram",
    "model": "nova-2",
    "language": "en",
}

TTS_CONFIG = {
    "provider": "cartesia",
    "voice_id": "a0e99841-438c-4a64-b679-ae501e7d6091",
    "model_id": "sonic-english",
}
```

### Mixed Configuration

You can mix and match! For example:
- Local STT + Cloud LLM + Local TTS
- Cloud STT + Cloud LLM + Cloud TTS

## Usage

### Start the server

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

### Client connection

Connect via WebSocket and send raw PCM audio (16-bit, 16kHz, mono):

```javascript
const ws = new WebSocket('ws://localhost:9000');

// Send audio chunks
ws.send(audioChunk);  // Raw PCM bytes

// Receive responses
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'audio') {
    const audioBytes = base64ToArrayBuffer(data.data);
    // Play audio
  }
};
```

## Supported Languages (Local STT)

Faster Whisper supports 99+ languages. Set `language` parameter:

```python
STT_CONFIG = {
    "provider": "local",
    "language": "es",  # Spanish
    # Or None for auto-detection
}
```

Common codes: `en`, `es`, `fr`, `de`, `it`, `pt`, `ru`, `ja`, `zh`, `ko`, `ar`, `hi`

## Performance

### Local Providers (CPU)
- **STT (Faster Whisper)**: 
  - `base` model: ~100-300ms latency
  - `tiny` model: ~50-100ms latency
  
- **TTS (Piper)**: 
  - ~50-200ms per sentence

### Cloud Providers
- **STT (Deepgram)**: ~50-150ms
- **TTS (Cartesia)**: ~100-300ms

Faster LLM models (gpt-4o-mini) reduce time to first audio significantly.

## Adding New Providers

### 1. Create provider class

Inherit from the base class in `providers/base.py`:

```python
# providers/stt_whisper_cpp.py
from .base import STTProvider

class WhisperCppSTT(STTProvider):
    async def transcribe_stream(self, audio_stream):
        # Your implementation
        pass
    
    async def close(self):
        pass
```

### 2. Add to factory

Edit `providers/factory.py`:

```python
elif provider == "whisper_cpp":
    from .stt_whisper_cpp import WhisperCppSTT
    return WhisperCppSTT(**kwargs)
```

### 3. Use in configuration

```python
STT_CONFIG = {
    "provider": "whisper_cpp",
    # Your config
}
```

## Project Structure

```
.
├── providers/
│   ├── __init__.py
│   ├── base.py              # Abstract base classes
│   ├── factory.py           # Provider factory
│   ├── stt_local.py         # Faster Whisper STT
│   ├── stt_deepgram.py      # Deepgram STT
│   ├── llm_openai.py        # OpenAI LLM
│   ├── tts_local.py         # Piper TTS
│   └── tts_cartesia.py      # Cartesia TTS
├── pipeline.py              # Main pipeline orchestration
├── server.py                # WebSocket server
├── requirements.txt
└── README.md
```

## Troubleshooting

### Faster Whisper model download fails
- Check internet connection
- Models are cached in `~/.cache/huggingface/`

### Piper model not found
- Ensure `.onnx` and `.onnx.json` files are in the same directory
- Provide absolute path to model

### High CPU usage
- Use smaller models: `tiny` for STT, smaller Piper voices
- Reduce `sample_rate` if possible

### Audio format issues
- Input must be 16-bit PCM, 16kHz, mono
- Output format varies by TTS provider (check `get_audio_format()`)

## License

MIT
