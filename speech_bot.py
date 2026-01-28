"""
End-to-End Speech Bot using Pipecat
Supports multiple providers for STT, LLM, and TTS
Focus on cost-effective, real-time solutions
"""

import asyncio
import aiohttp
import os
from pipecat.frames.frames import LLMMessagesFrame, EndFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.services.openai import OpenAILLMService
from pipecat.processors.aggregators.llm_response import LLMAssistantResponseAggregator, LLMUserResponseAggregator
from pipecat.transports.services.daily import DailyParams, DailyTransport

# Import various service options
try:
    from pipecat.services.deepgram import DeepgramSTTService, DeepgramTTSService
except ImportError:
    DeepgramSTTService = None
    DeepgramTTSService = None

try:
    from pipecat.services.cartesia import CartesiaTTSService
except ImportError:
    CartesiaTTSService = None

try:
    from pipecat.services.elevenlabs import ElevenLabsTTSService
except ImportError:
    ElevenLabsTTSService = None

try:
    from pipecat.services.rime import RimeAITTSService
except ImportError:
    RimeAITTSService = None


class SpeechBotConfig:
    """Configuration for speech bot with multiple provider options"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DAILY_API_KEY = os.getenv("DAILY_API_KEY")  # For WebRTC transport
    
    # STT Options (Speech-to-Text)
    STT_PROVIDER = os.getenv("STT_PROVIDER", "deepgram")  # deepgram, azure, whisper
    DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
    
    # TTS Options (Text-to-Speech)
    TTS_PROVIDER = os.getenv("TTS_PROVIDER", "cartesia")  # cartesia, elevenlabs, rime, deepgram
    CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    RIME_API_KEY = os.getenv("RIME_API_KEY")
    
    # LLM Options
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # openai, together, replicate
    TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")  # Cost-effective model


async def create_stt_service(config):
    """Create Speech-to-Text service based on provider"""
    
    if config.STT_PROVIDER == "deepgram":
        if not config.DEEPGRAM_API_KEY:
            raise ValueError("DEEPGRAM_API_KEY required for Deepgram STT")
        return DeepgramSTTService(api_key=config.DEEPGRAM_API_KEY)
    
    elif config.STT_PROVIDER == "whisper":
        # Using local Whisper or hosted Whisper API
        from pipecat.services.openai import OpenAISTTService
        return OpenAISTTService(
            api_key=config.OPENAI_API_KEY,
            model="whisper-1"
        )
    
    else:
        raise ValueError(f"Unsupported STT provider: {config.STT_PROVIDER}")


async def create_tts_service(config):
    """Create Text-to-Speech service based on provider"""
    
    if config.TTS_PROVIDER == "cartesia":
        # Cartesia - Very cost-effective and high quality
        if not config.CARTESIA_API_KEY:
            raise ValueError("CARTESIA_API_KEY required for Cartesia TTS")
        return CartesiaTTSService(
            api_key=config.CARTESIA_API_KEY,
            voice_id="a0e99841-438c-4a64-b679-ae501e7d6091"  # Conversational English
        )
    
    elif config.TTS_PROVIDER == "elevenlabs":
        # ElevenLabs - High quality but more expensive
        if not config.ELEVENLABS_API_KEY:
            raise ValueError("ELEVENLABS_API_KEY required for ElevenLabs TTS")
        return ElevenLabsTTSService(
            api_key=config.ELEVENLABS_API_KEY,
            voice_id="21m00Tcm4TlvDq8ikWAM"  # Rachel voice
        )
    
    elif config.TTS_PROVIDER == "rime":
        # Rime AI - Very cheap and fast
        if not config.RIME_API_KEY:
            raise ValueError("RIME_API_KEY required for Rime TTS")
        return RimeAITTSService(
            api_key=config.RIME_API_KEY,
            voice="amber"
        )
    
    elif config.TTS_PROVIDER == "deepgram":
        # Deepgram TTS - Good balance of cost and quality
        if not config.DEEPGRAM_API_KEY:
            raise ValueError("DEEPGRAM_API_KEY required for Deepgram TTS")
        return DeepgramTTSService(
            api_key=config.DEEPGRAM_API_KEY,
            voice="aura-asteria-en"
        )
    
    else:
        raise ValueError(f"Unsupported TTS provider: {config.TTS_PROVIDER}")


async def create_llm_service(config):
    """Create LLM service based on provider"""
    
    if config.LLM_PROVIDER == "openai":
        return OpenAILLMService(
            api_key=config.OPENAI_API_KEY,
            model=config.LLM_MODEL
        )
    
    elif config.LLM_PROVIDER == "together":
        # Together AI - Cheap hosted models
        from pipecat.services.together import TogetherLLMService
        return TogetherLLMService(
            api_key=config.TOGETHER_API_KEY,
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
        )
    
    else:
        raise ValueError(f"Unsupported LLM provider: {config.LLM_PROVIDER}")


async def main():
    """Main function to run the speech bot"""
    
    config = SpeechBotConfig()
    
    # Create services
    stt_service = await create_stt_service(config)
    tts_service = await create_tts_service(config)
    llm_service = await create_llm_service(config)
    
    # System prompt for the bot
    messages = [
        {
            "role": "system",
            "content": "You are a helpful voice assistant. Keep your responses concise and conversational since they will be spoken aloud."
        }
    ]
    
    # Create transport (Daily.co for WebRTC)
    transport = DailyTransport(
        config.DAILY_API_KEY,
        DailyParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            video_out_enabled=False,
            transcription_enabled=False,
        )
    )
    
    # Create aggregators
    user_response = LLMUserResponseAggregator(messages)
    assistant_response = LLMAssistantResponseAggregator(messages)
    
    # Build pipeline
    pipeline = Pipeline([
        transport.input(),           # Audio input
        stt_service,                 # Speech to text
        user_response,               # Aggregate user message
        llm_service,                 # LLM processing
        tts_service,                 # Text to speech
        transport.output(),          # Audio output
        assistant_response,          # Aggregate assistant message
    ])
    
    # Create and run task
    task = PipelineTask(pipeline)
    
    # Create room and get URL
    room_url = await transport.create_room()
    print(f"Join the conversation at: {room_url}")
    
    # Run the pipeline
    runner = PipelineRunner()
    await runner.run(task)


if __name__ == "__main__":
    asyncio.run(main())
