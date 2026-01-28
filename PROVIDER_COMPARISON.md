# Speech Bot Provider Comparison & Recommendations

## 🎯 Best Configurations by Use Case

### 1. CHEAPEST Option (Self-Hosted)
**Total Cost: ~$0.005/minute (only LLM costs)**

```yaml
STT: Faster Whisper (self-hosted, FREE)
TTS: Piper TTS (self-hosted, FREE)
LLM: OpenAI gpt-4o-mini ($0.15/$0.60 per 1M tokens)
Transport: WebSocket (FREE)
```

**Setup:**
```bash
pip install faster-whisper piper-tts openai websockets
python speech_bot_alternative.py
```

**Pros:**
- Almost free (only LLM costs)
- No API rate limits
- Privacy (audio stays local)
- Low latency

**Cons:**
- Requires decent CPU/GPU
- More complex setup
- Lower voice quality than commercial TTS

---

### 2. BEST VALUE Cloud Option
**Total Cost: ~$0.02/minute**

```yaml
STT: Deepgram ($0.0043/min)
TTS: Cartesia ($0.009/min)  
LLM: OpenAI gpt-4o-mini ($0.005/min avg)
Transport: Daily.co (FREE with limits)
```

**Setup:**
```bash
pip install pipecat-ai[daily,openai] deepgram-sdk cartesia
# Set API keys in .env
python speech_bot.py
```

**Pros:**
- Excellent quality
- Very low latency (<300ms)
- Scalable
- Easy setup

**Cons:**
- Monthly API costs
- Requires API keys

---

### 3. ALL OpenAI (Simplest)
**Total Cost: ~$0.03/minute**

```yaml
STT: OpenAI Whisper API ($0.006/min)
TTS: OpenAI TTS ($0.015/min)
LLM: OpenAI gpt-4o-mini ($0.005/min avg)
Transport: WebSocket (FREE)
```

**Setup:**
```bash
pip install openai websockets
# Only need OPENAI_API_KEY
python speech_bot_alternative.py
```

**Pros:**
- Single API key (you already have it!)
- Simple billing
- Good quality
- No extra signups

**Cons:**
- More expensive than alternatives
- Medium latency (~500ms)

---

## 📊 Detailed Provider Breakdown

### Speech-to-Text (STT)

#### Cloud Options:

**1. Deepgram** ⭐ RECOMMENDED
- Cost: $0.0043/minute
- Latency: <300ms
- Quality: Excellent
- Free tier: $200 credits
- Signup: https://console.deepgram.com/

**2. OpenAI Whisper API**
- Cost: $0.006/minute  
- Latency: ~500ms
- Quality: Excellent
- Free tier: No
- Already have key: YES

**3. AssemblyAI**
- Cost: $0.00025/second ($0.015/min)
- Latency: ~300ms
- Quality: Excellent
- Free tier: 100 hours
- Signup: https://www.assemblyai.com/

#### Self-Hosted Options:

**1. Faster Whisper** ⭐ RECOMMENDED (Self-hosted)
- Cost: FREE (your compute)
- Latency: ~200-500ms (depends on hardware)
- Quality: Excellent
- Requirements: 1-4GB RAM, works on CPU
```bash
pip install faster-whisper
```

**2. Whisper.cpp**
- Cost: FREE
- Latency: Very fast
- Quality: Excellent
- Requirements: C++ build, optimized for CPU

**3. Whisper JAX** 
- Cost: FREE
- Latency: Ultra-fast with GPU
- Quality: Excellent
- Requirements: GPU recommended

---

### Text-to-Speech (TTS)

#### Cloud Options:

**1. Cartesia** ⭐ RECOMMENDED
- Cost: $0.00015/second (~$0.009/min)
- Latency: <300ms
- Quality: Excellent (neural, natural)
- Free tier: $10 credits
- Signup: https://play.cartesia.ai/
- Best feature: Streaming support

**2. Rime AI** (Cheapest Cloud)
- Cost: $0.0001/second (~$0.006/min)
- Latency: <200ms
- Quality: Good
- Free tier: Limited
- Signup: https://rime.ai/

**3. OpenAI TTS**
- Cost: $0.015/1K characters (~$0.015/min)
- Latency: ~500ms
- Quality: Good
- Free tier: No
- Already have key: YES
- Models: tts-1 (fast), tts-1-hd (quality)

**4. Deepgram Aura**
- Cost: $0.015/1K characters
- Latency: <300ms
- Quality: Good
- Free tier: $200 credits (same as STT)

**5. ElevenLabs** (Premium)
- Cost: $0.24/1K characters (~$0.50/min)
- Latency: ~400ms
- Quality: Excellent (most natural)
- Free tier: 10K chars/month
- Signup: https://elevenlabs.io/

#### Self-Hosted Options:

**1. Piper** ⭐ RECOMMENDED (Self-hosted)
- Cost: FREE
- Latency: <100ms
- Quality: Good
- Requirements: Lightweight, CPU only
```bash
pip install piper-tts
# Download voice: wget https://github.com/rhasspy/piper/releases/
```

**2. Coqui TTS**
- Cost: FREE
- Latency: ~500ms
- Quality: Good to Excellent
- Requirements: 2-4GB RAM
```bash
pip install TTS
```

**3. Bark**
- Cost: FREE
- Latency: Slow (seconds)
- Quality: Very natural
- Requirements: GPU recommended
```bash
pip install bark
```

---

### Large Language Models (LLM)

#### Cloud Options:

**1. OpenAI gpt-4o-mini** ⭐ RECOMMENDED (You have this!)
- Cost: $0.15 input / $0.60 output per 1M tokens
- Speed: Fast
- Quality: Excellent
- Context: 128K tokens

**2. OpenAI gpt-3.5-turbo**
- Cost: $0.50 input / $1.50 output per 1M tokens
- Speed: Very fast
- Quality: Good
- Context: 16K tokens

**3. Groq** (Fastest)
- Cost: $0.05 input / $0.08 output per 1M tokens
- Speed: Ultra-fast (600+ tokens/sec)
- Quality: Good
- Models: Llama 3.1, Mixtral
- Signup: https://console.groq.com/
- Best feature: Speed

**4. Together AI** (Open Source Models)
- Cost: $0.18-$0.88 per 1M tokens
- Speed: Fast
- Quality: Good to Excellent
- Models: Llama 3.1, Mixtral, Qwen
- Signup: https://www.together.ai/

**5. Anthropic Claude** (If you want variety)
- Cost: Varies by model
- Speed: Fast
- Quality: Excellent
- Best feature: Long context

#### Self-Hosted Options:

**1. Ollama** ⭐ RECOMMENDED (Self-hosted)
- Cost: FREE
- Speed: Fast (depends on hardware)
- Quality: Good to Excellent
- Requirements: 8GB+ RAM
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:8b
```

**2. vLLM**
- Cost: FREE
- Speed: Very fast with GPU
- Quality: Excellent
- Requirements: GPU with 16GB+ VRAM
```bash
pip install vllm
```

**3. llama.cpp**
- Cost: FREE
- Speed: Fast on CPU
- Quality: Good to Excellent
- Requirements: CPU only
```bash
# Runs quantized models efficiently
```

---

### Transport Layer

**1. Daily.co** ⭐ RECOMMENDED
- Cost: FREE (up to 10K minutes/month)
- Latency: <100ms
- Setup: Easy
- Signup: https://daily.co/
- Best feature: WebRTC built-in

**2. WebSocket** (Simple)
- Cost: FREE
- Latency: Varies
- Setup: Very easy
- Requirements: Just Python

**3. Twilio**
- Cost: $0.0085/minute
- Latency: Low
- Setup: Moderate
- Best feature: Phone integration

**4. Agora**
- Cost: $0.99/1000 minutes
- Latency: Very low
- Setup: Moderate
- Best feature: Low latency globally

---

## 💡 Recommended Setups

### For Hobbyist/Testing ($0/month base)
```
STT: Faster Whisper (self-hosted)
TTS: Piper (self-hosted)
LLM: Ollama (self-hosted)
Transport: WebSocket
```

### For Side Project (<$20/month)
```
STT: Deepgram ($200 free credits = ~46K minutes!)
TTS: Cartesia ($10 free credits = ~11K minutes)
LLM: gpt-4o-mini (You already have)
Transport: Daily.co (free tier)
```

### For Production (Scalable)
```
STT: Deepgram
TTS: Cartesia or ElevenLabs
LLM: gpt-4o-mini or Claude
Transport: Daily.co or Agora
Monitoring: Add Datadog/Sentry
```

### For Privacy-First
```
STT: Faster Whisper (self-hosted)
TTS: Piper (self-hosted)
LLM: Ollama (self-hosted)
Transport: WebSocket (self-hosted)
```

---

## 🚀 Getting Started Steps

### Option 1: Pipecat with Cloud Services (Easiest)

1. **Sign up for free credits:**
   - Deepgram: https://console.deepgram.com/ ($200 free)
   - Cartesia: https://play.cartesia.ai/ ($10 free)
   - Daily.co: https://daily.co/ (10K minutes free/month)

2. **Install:**
   ```bash
   pip install pipecat-ai[daily,openai] deepgram-sdk cartesia
   ```

3. **Configure .env:**
   ```bash
   OPENAI_API_KEY=your_key
   DEEPGRAM_API_KEY=your_key
   CARTESIA_API_KEY=your_key
   DAILY_API_KEY=your_key
   ```

4. **Run:**
   ```bash
   python speech_bot.py
   ```

### Option 2: All Self-Hosted (Cheapest)

1. **Install:**
   ```bash
   pip install faster-whisper piper-tts openai websockets
   
   # Download Piper voice
   wget https://github.com/rhasspy/piper/releases/download/v1.2.0/en_US-lessac-medium.onnx
   
   # Install Ollama (optional)
   curl -fsSL https://ollama.com/install.sh | sh
   ollama pull llama3.1:8b
   ```

2. **Configure .env:**
   ```bash
   OPENAI_API_KEY=your_key  # Only for LLM
   ```

3. **Run:**
   ```bash
   python speech_bot_alternative.py
   ```

### Option 3: All OpenAI (Simplest)

1. **Install:**
   ```bash
   pip install openai websockets
   ```

2. **Configure .env:**
   ```bash
   OPENAI_API_KEY=your_key  # That's it!
   ```

3. **Run:**
   ```bash
   python speech_bot_alternative.py
   ```

---

## 📈 Cost Calculator

**Example: 1000 minutes of conversation per month**

| Component | Cheapest | Balanced | Premium |
|-----------|----------|----------|---------|
| STT | Free (self) / $4.30 | $4.30 | $4.30 |
| TTS | Free (self) / $6 | $9 | $500 |
| LLM | $5 | $5 | $20 |
| **Total** | **$0-15** | **$18** | **$524** |

---

## 🎓 Learning Resources

- Pipecat Docs: https://docs.pipecat.ai/
- Deepgram Guide: https://developers.deepgram.com/docs/getting-started
- Faster Whisper: https://github.com/guillaumekln/faster-whisper
- Piper TTS: https://github.com/rhasspy/piper
- Ollama: https://ollama.com/library

---

## ✅ Quick Decision Matrix

**Choose Pipecat + Cloud if:**
- You want easiest setup
- You need production quality
- Budget is <$50/month
- You want to scale easily

**Choose Self-Hosted if:**
- Budget is $0
- You have decent hardware (8GB+ RAM)
- Privacy is critical
- You're comfortable with CLI

**Choose All-OpenAI if:**
- You want simplest setup
- You already have OpenAI key
- You need just text or simple voice
- Budget is flexible
