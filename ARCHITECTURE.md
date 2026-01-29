# Voice Assistant Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      WebSocket Client                            │
│                   (Browser/Mobile App)                           │
└───────────────┬─────────────────────────┬───────────────────────┘
                │                         │
                │ PCM Audio (16kHz)       │ MP3/WAV Audio
                ▼                         ▲
┌─────────────────────────────────────────────────────────────────┐
│                      WebSocket Server                            │
│                        (server.py)                               │
└───────────────┬─────────────────────────┬───────────────────────┘
                │                         │
                ▼                         ▲
┌─────────────────────────────────────────────────────────────────┐
│                      Voice Pipeline                              │
│                       (pipeline.py)                              │
│                                                                  │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐           │
│  │    STT     │───▶│    LLM     │───▶│    TTS     │           │
│  │  Provider  │    │  Provider  │    │  Provider  │           │
│  └────────────┘    └────────────┘    └────────────┘           │
│         │                 │                 │                   │
└─────────┼─────────────────┼─────────────────┼───────────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                      Provider Implementations                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  STT Providers:              LLM Providers:      TTS Providers:  │
│  ┌──────────────┐           ┌──────────────┐   ┌─────────────┐ │
│  │ Faster       │           │   OpenAI     │   │   Piper     │ │
│  │ Whisper      │           │  (GPT-4o)    │   │  (Local)    │ │
│  │ (Local/CPU)  │           │              │   │             │ │
│  └──────────────┘           └──────────────┘   └─────────────┘ │
│                                                                   │
│  ┌──────────────┐                               ┌─────────────┐ │
│  │  Deepgram    │                               │  Cartesia   │ │
│  │   (Cloud)    │                               │   (Cloud)   │ │
│  └──────────────┘                               └─────────────┘ │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Request Flow (User speaks)
```
1. Client captures microphone audio
   └─▶ Sends PCM chunks via WebSocket

2. Server receives audio
   └─▶ Pipeline.run() starts

3. STT Provider processes audio stream
   └─▶ Yields transcribed text when speech ends

4. LLM Provider generates response
   └─▶ Streams tokens as they're generated

5. Pipeline buffers tokens until punctuation
   └─▶ Sends sentence chunks to TTS

6. TTS Provider synthesizes each sentence
   └─▶ Returns audio bytes (MP3/WAV)

7. Server sends audio to client
   └─▶ Client plays audio
```

### Component Responsibilities

**WebSocket Server** (`server.py`)
- Accept client connections
- Route audio streams to pipeline
- Send responses back to client
- Handle connection lifecycle

**Voice Pipeline** (`pipeline.py`)
- Orchestrate STT → LLM → TTS flow
- Buffer LLM tokens until punctuation
- Track timing metrics
- Manage streaming state

**Provider Interfaces** (`providers/base.py`)
- Define abstract contracts
- `STTProvider`: audio bytes → text
- `LLMProvider`: text → token stream
- `TTSProvider`: text → audio bytes

**Provider Factory** (`providers/factory.py`)
- Instantiate providers from config
- Load API keys from environment
- Handle provider-specific setup

## Switching Providers

All providers implement the same interface, so switching is just configuration:

```python
# Use local Whisper
STT_CONFIG = {"provider": "local", "model_size": "base"}

# Switch to Deepgram  
STT_CONFIG = {"provider": "deepgram", "model": "nova-2"}
```

No code changes needed!

## Extending the System

### Adding a New STT Provider

1. Create `providers/stt_yourprovider.py`
2. Inherit from `STTProvider`
3. Implement `transcribe_stream()` and `close()`
4. Add to `ProviderFactory.create_stt()`

### Adding a New LLM Provider

1. Create `providers/llm_yourprovider.py`
2. Inherit from `LLMProvider`
3. Implement `generate_stream()`
4. Add to `ProviderFactory.create_llm()`

### Adding a New TTS Provider

1. Create `providers/tts_yourprovider.py`
2. Inherit from `TTSProvider`
3. Implement `synthesize()` and `get_audio_format()`
4. Add to `ProviderFactory.create_tts()`
