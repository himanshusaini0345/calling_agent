"""
Speech Bot with GROQ for Ultra-Fast LLM Responses
Groq delivers 600+ tokens/second - much faster than OpenAI

Recommended config for speed:
- STT: Deepgram (fastest)
- LLM: Groq (fastest - 600+ tok/s vs OpenAI's 50 tok/s)
- TTS: Cartesia (fastest streaming)
"""

import asyncio
import os
from pipecat.frames.frames import EndFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.processors.aggregators.llm_response import (
    LLMAssistantResponseAggregator,
    LLMUserResponseAggregator,
)
from pipecat.services.deepgram import DeepgramSTTService, DeepgramTTSService
from pipecat.services.cartesia import CartesiaTTSService
from pipecat.transports.services.daily import DailyParams, DailyTransport

# Groq LLM Service
try:
    from groq import AsyncGroq
except ImportError:
    print("Install groq: pip install groq")
    AsyncGroq = None


class GroqLLMService:
    """Custom Groq LLM service for Pipecat"""
    
    def __init__(self, api_key: str, model: str = "llama-3.1-8b-instant"):
        if not AsyncGroq:
            raise ImportError("groq package not installed")
        
        self.client = AsyncGroq(api_key=api_key)
        self.model = model
        self._messages = []
    
    async def process_frame(self, frame):
        """Process incoming frames"""
        # Handle user messages
        if hasattr(frame, 'messages'):
            self._messages = frame.messages
            
            # Get completion from Groq
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=self._messages,
                temperature=0.7,
                max_tokens=200,  # Keep responses concise for voice
            )
            
            assistant_message = response.choices[0].message.content
            
            # Return assistant message frame
            return assistant_message
        
        return frame


async def main():
    """Run ultra-fast speech bot with Groq"""
    
    # Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
    CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY")
    DAILY_API_KEY = os.getenv("DAILY_API_KEY")
    
    if not all([GROQ_API_KEY, DEEPGRAM_API_KEY, CARTESIA_API_KEY]):
        print("Missing API keys!")
        print("Get Groq key (FREE): https://console.groq.com/")
        print("Get Deepgram ($200 free): https://console.deepgram.com/")
        print("Get Cartesia ($10 free): https://play.cartesia.ai/")
        return
    
    # System prompt
    messages = [
        {
            "role": "system",
            "content": "You are a helpful voice assistant. Be concise and natural."
        }
    ]
    
    # Create services
    stt = DeepgramSTTService(api_key=DEEPGRAM_API_KEY)
    
    # Groq for ultra-fast LLM (600+ tokens/second!)
    llm = GroqLLMService(
        api_key=GROQ_API_KEY,
        model="llama-3.1-8b-instant"  # Fastest Groq model
    )
    
    # Cartesia for low-latency TTS with streaming
    tts = CartesiaTTSService(
        api_key=CARTESIA_API_KEY,
        voice_id="a0e99841-438c-4a64-b679-ae501e7d6091",  # British Lady
        # Other great voices:
        # "694f9389-aac1-45b6-b726-9d9369183238" - Calm Lady
        # "79a125e8-cd45-4c13-8a67-188112f4dd22" - Friendly Reading Man
    )
    
    # WebRTC transport
    transport = DailyTransport(
        DAILY_API_KEY,
        DailyParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            transcription_enabled=False,
            vad_enabled=True,  # Voice activity detection
        ),
    )
    
    # Aggregators
    user_response = LLMUserResponseAggregator(messages)
    assistant_response = LLMAssistantResponseAggregator(messages)
    
    # Build pipeline
    pipeline = Pipeline(
        [
            transport.input(),
            stt,
            user_response,
            llm,
            tts,
            transport.output(),
            assistant_response,
        ]
    )
    
    # Create task
    task = PipelineTask(pipeline)
    
    # Get room URL
    room_url = await transport.create_room()
    print(f"\n🚀 Ultra-Fast Speech Bot Ready!")
    print(f"📊 Speed: ~600 tokens/sec (Groq) vs ~50 tokens/sec (OpenAI)")
    print(f"🔗 Join at: {room_url}\n")
    
    # Run
    runner = PipelineRunner()
    await runner.run(task)


# Available Groq Models (all ultra-fast):
GROQ_MODELS = {
    "llama-3.1-8b-instant": "Fastest, great quality",
    "llama-3.1-70b-versatile": "Best quality, still very fast",
    "mixtral-8x7b-32768": "Good balance, 32K context",
    "gemma2-9b-it": "Google's model, fast",
}


if __name__ == "__main__":
    print("\n⚡ GROQ-POWERED SPEECH BOT ⚡")
    print("Expected latency: <500ms total")
    print("- Deepgram STT: ~300ms")
    print("- Groq LLM: ~50ms (for 100 tokens)")
    print("- Cartesia TTS: ~150ms\n")
    
    asyncio.run(main())
