# Cloud-Hosted Open Source Models Guide

## 🌐 Why Cloud-Hosted Open Source?

Benefits:
- ✅ No server maintenance
- ✅ Pay only for usage
- ✅ Instant scaling
- ✅ No GPU required locally
- ✅ Often cheaper than commercial APIs

## 🚀 Best Platforms for Open Source Models

### 1. Together AI ⭐ RECOMMENDED

**What it is:** Cloud platform hosting 50+ open source models

**Pricing:**
- Llama 3.1 8B: $0.18/$0.18 per 1M tokens
- Llama 3.1 70B: $0.88/$0.88 per 1M tokens
- Mixtral 8x7B: $0.60/$0.60 per 1M tokens
- Qwen 2.5: $0.30/$0.30 per 1M tokens

**Setup:**
```bash
pip install together

# Get API key at https://api.together.xyz/
```

**Usage with Pipecat:**
```python
from together import AsyncTogether
import os

class TogetherLLMService:
    def __init__(self):
        self.client = AsyncTogether(api_key=os.getenv("TOGETHER_API_KEY"))
    
    async def generate(self, messages):
        response = await self.client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            messages=messages,
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content

# Use in your speech bot
llm = TogetherLLMService()
```

**Best models:**
- `meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo` - Fast, cheap
- `meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo` - Best quality
- `mistralai/Mixtral-8x7B-Instruct-v0.1` - Great balance
- `Qwen/Qwen2.5-72B-Instruct-Turbo` - Excellent reasoning

---

### 2. Groq 🚀 FASTEST

**What it is:** Ultra-fast inference (600+ tokens/sec)

**Pricing:**
- Llama 3.1 8B: $0.05/$0.08 per 1M tokens
- Llama 3.1 70B: $0.59/$0.79 per 1M tokens
- Mixtral 8x7B: $0.24/$0.24 per 1M tokens

**Speed:** 10-20x faster than other providers!

**Setup:**
```bash
pip install groq

# Get FREE API key at https://console.groq.com/
```

**Usage:**
```python
from groq import AsyncGroq
import os

class GroqLLMService:
    def __init__(self):
        self.client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
    
    async def generate(self, messages):
        response = await self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            max_tokens=200
        )
        return response.choices[0].message.content
```

**Why Groq?**
- 600+ tokens/second (vs OpenAI's 50)
- Perfect for real-time voice bots
- FREE tier available
- See full example in `speech_bot_groq.py`

---

### 3. Replicate

**What it is:** Run ML models via API

**Pricing:** Pay per second of inference
- Llama 3.1 8B: ~$0.05 per 1M tokens
- Flux (image gen): $0.0025 per image

**Setup:**
```bash
pip install replicate

# Get API key at https://replicate.com/
```

**Usage:**
```python
import replicate
import os

async def generate_with_llama(prompt):
    output = await replicate.async_run(
        "meta/meta-llama-3.1-8b-instruct",
        input={
            "prompt": prompt,
            "max_tokens": 200
        }
    )
    return "".join(output)
```

**Also great for:**
- Image generation (Flux, SDXL)
- Audio generation (MusicGen)
- Video generation

---

### 4. Fireworks AI

**What it is:** Fast inference for LLMs

**Pricing:**
- Llama 3.1 8B: $0.20/$0.20 per 1M tokens
- Llama 3.1 70B: $0.90/$0.90 per 1M tokens
- Mixtral: $0.50/$0.50 per 1M tokens

**Setup:**
```bash
pip install fireworks-ai

# Get API key at https://fireworks.ai/
```

**Usage:**
```python
from fireworks.client import AsyncFireworks

client = AsyncFireworks(api_key=os.getenv("FIREWORKS_API_KEY"))

response = await client.chat.completions.create(
    model="accounts/fireworks/models/llama-v3p1-8b-instruct",
    messages=messages
)
```

---

### 5. Anyscale Endpoints

**What it is:** Ray-powered model serving

**Pricing:**
- Llama 3.1 8B: $0.15/$0.15 per 1M tokens
- Llama 3.1 70B: $1.00/$1.00 per 1M tokens

**Setup:**
```bash
pip install openai  # Uses OpenAI SDK

# Get API key at https://app.endpoints.anyscale.com/
```

**Usage:**
```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    base_url="https://api.endpoints.anyscale.com/v1",
    api_key=os.getenv("ANYSCALE_API_KEY")
)

response = await client.chat.completions.create(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct",
    messages=messages
)
```

---

### 6. Modal (Serverless GPU)

**What it is:** Run your own models on serverless GPUs

**Pricing:** Pay per second of GPU usage
- T4 GPU: $0.00040/sec (~$1.44/hour)
- A10G GPU: $0.00150/sec (~$5.40/hour)
- A100 GPU: $0.00400/sec (~$14.40/hour)

**Setup:**
```bash
pip install modal

# Sign up at https://modal.com/
```

**Example - Deploy Llama:**
```python
import modal

stub = modal.Stub("llama-api")

@stub.function(
    gpu="T4",
    image=modal.Image.from_registry("nvidia/cuda:12.1.0-base-ubuntu22.04")
        .pip_install("vllm")
)
def generate(prompt: str):
    from vllm import LLM
    
    llm = LLM("meta-llama/Meta-Llama-3.1-8B-Instruct")
    output = llm.generate(prompt)
    return output[0].outputs[0].text

# Deploy
modal deploy llama_api.py
```

**Best for:**
- Custom model hosting
- Fine-tuned models
- Complete control

---

### 7. RunPod (GPU Rental)

**What it is:** Rent GPUs by the minute

**Pricing:**
- RTX 4090: $0.34/hour
- A40: $0.79/hour  
- A100 80GB: $1.89/hour

**Setup:**
1. Go to https://runpod.io/
2. Choose a GPU
3. Deploy a template (Whisper, Llama, etc.)

**Great for:**
- Long-running jobs
- Heavy models
- Batch processing

---

### 8. HuggingFace Inference API

**What it is:** Run any HF model via API

**Pricing:**
- Free tier: 1000 requests/day
- Pro: $9/month for 100K requests
- Enterprise: Custom

**Setup:**
```bash
pip install huggingface_hub

# Get API key at https://huggingface.co/settings/tokens
```

**Usage:**
```python
from huggingface_hub import AsyncInferenceClient

client = AsyncInferenceClient(
    token=os.getenv("HF_TOKEN")
)

response = await client.text_generation(
    "meta-llama/Meta-Llama-3.1-8B-Instruct",
    prompt="Hello!",
    max_new_tokens=200
)
```

**Supports:**
- 100K+ models
- Text, image, audio
- Custom models

---

## 💰 Cost Comparison (per 1M tokens)

| Provider | Llama 3.1 8B | Llama 3.1 70B | Speed | Free Tier |
|----------|--------------|---------------|-------|-----------|
| **Groq** | $0.05/$0.08 | $0.59/$0.79 | ⚡⚡⚡⚡⚡ | Yes |
| **Together** | $0.18/$0.18 | $0.88/$0.88 | ⚡⚡⚡ | $25 |
| Fireworks | $0.20/$0.20 | $0.90/$0.90 | ⚡⚡⚡⚡ | $1 |
| Anyscale | $0.15/$0.15 | $1.00/$1.00 | ⚡⚡⚡ | $10 |
| Replicate | ~$0.05 | - | ⚡⚡ | No |
| HuggingFace | Free* | Free* | ⚡ | 1K/day |

*Limited requests on free tier

---

## 🎯 Recommendations by Use Case

### For Voice Bots (Speed Critical)
**Winner: Groq** 🏆
- 600+ tokens/second
- Perfect for real-time
- Cheapest option
- FREE tier available

```python
# See speech_bot_groq.py for full example
from groq import AsyncGroq

llm = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
```

### For Best Quality
**Winner: Together AI** 🏆
- Access to largest models
- Llama 3.1 405B available
- Great selection
- Reasonable pricing

```python
from together import AsyncTogether

llm = AsyncTogether(api_key=os.getenv("TOGETHER_API_KEY"))
response = await llm.chat.completions.create(
    model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
    messages=messages
)
```

### For Cheapest
**Winner: HuggingFace Free Tier** 🏆
- 1000 requests/day free
- Access to all models
- Great for testing

### For Custom Models
**Winner: Modal** 🏆
- Deploy your own models
- Serverless GPU
- Pay per second

---

## 🔧 Integration Example

Here's a complete example using Together AI:

```python
"""
Speech bot with Together AI (open source models)
"""

import asyncio
import os
from together import AsyncTogether
from pipecat.services.deepgram import DeepgramSTTService
from pipecat.services.cartesia import CartesiaTTSService
from pipecat.pipeline.pipeline import Pipeline
from pipecat.transports.services.daily import DailyTransport, DailyParams

class TogetherLLMService:
    """Together AI service for Pipecat"""
    
    def __init__(self, api_key: str, model: str):
        self.client = AsyncTogether(api_key=api_key)
        self.model = model
        self._messages = []
    
    async def process_frame(self, frame):
        if hasattr(frame, 'messages'):
            self._messages = frame.messages
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=self._messages,
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        
        return frame

async def main():
    # Services
    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
    
    llm = TogetherLLMService(
        api_key=os.getenv("TOGETHER_API_KEY"),
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
    )
    
    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="a0e99841-438c-4a64-b679-ae501e7d6091"
    )
    
    transport = DailyTransport(
        os.getenv("DAILY_API_KEY"),
        DailyParams(audio_in_enabled=True, audio_out_enabled=True)
    )
    
    # Build pipeline
    pipeline = Pipeline([
        transport.input(),
        stt,
        llm,
        tts,
        transport.output()
    ])
    
    # Run
    room_url = await transport.create_room()
    print(f"Join at: {room_url}")
    
    await pipeline.run()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📊 Which Platform Should You Choose?

**Start with Groq if:**
- You need speed (voice bots)
- You want free tier
- You're okay with smaller models

**Use Together AI if:**
- You want largest model selection
- You need 70B+ models
- You want good balance

**Try HuggingFace if:**
- You're just testing
- You want free tier
- You're okay with rate limits

**Consider Modal if:**
- You have custom models
- You need full control
- You want to fine-tune

---

## 💡 Pro Tips

1. **Start with free tiers** - Test before committing
2. **Monitor costs** - Add usage tracking
3. **Cache responses** - Save on common queries
4. **Use smaller models** - 8B is often enough
5. **Batch requests** - When possible
6. **Set max_tokens** - Control costs
7. **Add timeouts** - Prevent hanging requests

---

## 🔗 Resources

- Together AI: https://www.together.ai/
- Groq: https://groq.com/
- Replicate: https://replicate.com/
- Modal: https://modal.com/
- HuggingFace: https://huggingface.co/
- Fireworks: https://fireworks.ai/
- Anyscale: https://www.anyscale.com/

---

## 📈 Monthly Cost Examples

For **10,000 conversations** (~5M tokens):

| Platform | Model | Cost |
|----------|-------|------|
| Groq | Llama 3.1 8B | $0.40 |
| Together | Llama 3.1 8B | $0.90 |
| Together | Llama 3.1 70B | $4.40 |
| OpenAI | gpt-4o-mini | $7.50 |
| OpenAI | gpt-4o | $50.00 |

**Groq is 18x cheaper than gpt-4o for similar quality!**
