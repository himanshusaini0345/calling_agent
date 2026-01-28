# End-to-End Speech Bot with Pipecat

A real-time voice conversation bot using Pipecat framework with cost-effective, open-source friendly options.

## 🎯 Features

- **Real-time voice conversations** via WebRTC (Daily.co)
- **Multiple provider options** for STT, TTS, and LLM
- **Cost-optimized** configurations
- **Easy to deploy** and customize

## 📊 Cost Comparison

### Speech-to-Text (STT)
| Provider | Cost | Quality | Speed | Free Tier |
|----------|------|---------|-------|-----------|
| **Deepgram** | $0.0043/min | Excellent | Very Fast | $200 credits |
| Whisper (OpenAI) | $0.006/min | Excellent | Fast | No |
| Azure Speech | $1/hour | Excellent | Fast | 5 hours/month |

**Recommendation**: Deepgram (best balance)

### Text-to-Speech (TTS)
| Provider | Cost | Quality | Latency | Free Tier |
|----------|------|---------|---------|-----------|
| **Cartesia** | $0.00015/sec (~$0.009/min) | Excellent | <300ms | $10 credits |
| Rime AI | $0.0001/sec (~$0.006/min) | Good | <200ms | Limited |
| Deepgram | $0.015/1K chars (~$0.03/min) | Good | <300ms | $200 credits |
| ElevenLabs | $0.24/1K chars (~$0.50/min) | Excellent | ~400ms | 10K chars/month |
| Coqui TTS | Free (self-hosted) | Good | Varies | N/A |

**Recommendation**: Cartesia (best quality/cost) or Rime AI (cheapest)

### LLM Options
| Provider | Model | Cost | Quality | Speed |
|----------|-------|------|---------|-------|
| **OpenAI** | gpt-4o-mini | $0.15/$0.60 per 1M tokens | Excellent | Fast |
| OpenAI | gpt-3.5-turbo | $0.50/$1.50 per 1M tokens | Good | Very Fast |
| Together AI | Llama-3.1-8B | $0.18/$0.18 per 1M tokens | Good | Fast |
| Together AI | Llama-3.1-70B | $0.88/$0.88 per 1M tokens | Excellent | Fast |
| Groq | Llama-3.1-8B | $0.05/$0.08 per 1M tokens | Good | Very Fast |

**Recommendation**: gpt-4o-mini (excellent balance) or Together AI for open source

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Keys

Copy `.env.example` to `.env` and add your keys:

```bash
cp .env.example .env
```

**Required Keys:**
- **OpenAI API Key**: Get at https://platform.openai.com/api-keys
- **Daily.co API Key**: Get free at https://dashboard.daily.co/developers

**Choose ONE STT Provider:**
- **Deepgram** (Recommended): https://console.deepgram.com/ - $200 free credits

**Choose ONE TTS Provider:**
- **Cartesia** (Recommended): https://play.cartesia.ai/ - $10 free credits
- **Rime AI**: https://rime.ai/ - Very cheap
- **Deepgram**: Use same key as STT

### 3. Run the Bot

```bash
python speech_bot.py
```

You'll get a URL to join the conversation via web browser.

## 💰 Cost-Optimized Configurations

### Ultra-Cheap Setup (~$0.02/minute)
```env
STT_PROVIDER=deepgram
TTS_PROVIDER=rime
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
```

### Balanced Setup (~$0.03/minute)
```env
STT_PROVIDER=deepgram
TTS_PROVIDER=cartesia
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
```

### Premium Quality Setup (~$0.55/minute)
```env
STT_PROVIDER=deepgram
TTS_PROVIDER=elevenlabs
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
```

## 🔧 Alternative LLM Providers

### Using Together AI (Open Source Models)

```python
# In your .env
LLM_PROVIDER=together
TOGETHER_API_KEY=your_key
```

Install Together AI:
```bash
pip install together
```

**Available Models:**
- `meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo` - Fast and cheap
- `meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo` - High quality
- `mistralai/Mixtral-8x7B-Instruct-v0.1` - Good balance

### Using Groq (Ultra-Fast)

```bash
pip install groq
```

```python
from pipecat.services.groq import GroqLLMService

llm = GroqLLMService(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant"
)
```

### Self-Hosted Options

**Ollama (Free, Local)**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3.1:8b

# Use in Pipecat
pip install ollama
```

**vLLM (Fast self-hosted)**
```bash
pip install vllm
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Meta-Llama-3.1-8B-Instruct
```

## 🎤 Alternative STT Options

### Self-Hosted Whisper (Free)

```bash
pip install openai-whisper
```

```python
from pipecat.services.whisper import WhisperSTTService

stt = WhisperSTTService(
    model="base"  # Options: tiny, base, small, medium, large
)
```

### Faster-Whisper (Optimized)

```bash
pip install faster-whisper
```

Much faster than standard Whisper with same quality.

## 🔊 Alternative TTS Options

### Self-Hosted Coqui TTS (Free)

```bash
pip install TTS
```

```python
from TTS.api import TTS

tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
```

### Piper TTS (Fast & Free)

```bash
pip install piper-tts
```

Very fast, lightweight, runs on CPU.

## 🌐 Cloud-Hosted Open Source Models

### RunPod (GPU Instances)
- Deploy Whisper, TTS models on demand
- Pay per minute of GPU usage
- https://runpod.io/

### Replicate
- Pre-deployed open source models
- Pay per API call
- https://replicate.com/

### Modal
- Serverless GPU functions
- Great for TTS/STT models
- https://modal.com/

### HuggingFace Inference
- Hosted open source models
- Free tier available
- https://huggingface.co/inference-api

## 📝 Advanced Configuration

### Custom System Prompt

Edit the `messages` list in `speech_bot.py`:

```python
messages = [
    {
        "role": "system",
        "content": "You are a friendly customer service bot. Be helpful and concise."
    }
]
```

### Using WebSocket Instead of Daily

```python
from pipecat.transports.websocket import WebsocketTransport

transport = WebsocketTransport(
    host="0.0.0.0",
    port=8765
)
```

### Adding Memory/Context

```python
# Store conversation history
conversation_history = []

# Add to aggregators
user_response = LLMUserResponseAggregator(
    messages=messages,
    history=conversation_history
)
```

## 🔒 Production Considerations

1. **Rate Limiting**: Add rate limits to prevent abuse
2. **Authentication**: Implement user authentication
3. **Monitoring**: Track usage and costs
4. **Error Handling**: Add retry logic and fallbacks
5. **Caching**: Cache TTS responses for common phrases

## 📚 Resources

- **Pipecat Docs**: https://docs.pipecat.ai/
- **Daily.co Docs**: https://docs.daily.co/
- **Deepgram Docs**: https://developers.deepgram.com/
- **Cartesia Docs**: https://docs.cartesia.ai/

## 💡 Tips

1. **Start with free tiers** to test before scaling
2. **Cartesia** offers best TTS quality/cost ratio
3. **Deepgram** has generous free credits for STT
4. **gpt-4o-mini** is 10x cheaper than GPT-4 with great quality
5. Use **WebRTC** (Daily) for lowest latency
6. Consider **self-hosted** options for high-volume use

## 🐛 Troubleshooting

**Audio issues?**
- Check microphone permissions in browser
- Ensure Daily.co room is created successfully

**High latency?**
- Use Cartesia or Rime for TTS (lowest latency)
- Consider regional API endpoints

**Rate limits?**
- Add delays between requests
- Implement queuing for high traffic

## 📊 Estimated Monthly Costs

For a bot handling **1000 minutes/month** of conversation:

| Configuration | STT | TTS | LLM | Total/month |
|--------------|-----|-----|-----|-------------|
| Ultra-Cheap | $4.30 | $6 | $5 | **~$15** |
| Balanced | $4.30 | $9 | $5 | **~$18** |
| Premium | $4.30 | $500 | $20 | **~$524** |

*LLM costs assume ~1000 tokens per conversation*

## 📄 License

MIT License - feel free to use in commercial projects!
