"""Provider factory for easy instantiation."""

from src.llm.llm_provider import LLMProvider
from src.llm.openai import OpenAILLM
from src.stt.deepgram import DeepgramSTT
from src.stt.faster_whisper import FasterWhisperSTT
from src.stt.indic_conformer import IndicConformerSTT
from src.stt.stt_provider import STTProvider
from src.tts.azure import AzureTTS
from src.tts.cartesia import CartesiaTTS
from src.tts.coqui import CoquiTTS
from src.tts.edge import EdgeTTS
from src.tts.espeak import EspeakTTS
from src.tts.openai import OpenAITTS
from src.tts.piper import PiperTTS
from src.tts.tts_provider import TTSProvider


class ProviderFactory:
    """Factory for creating provider instances."""
    
    @staticmethod
    def create_stt(
        provider: str,
        **kwargs
    ) -> STTProvider:
        """
        Create STT provider.
        
        Args:
            provider: "local" (Faster Whisper) or "deepgram"
            **kwargs: Provider-specific arguments
        """
        if provider == "local":
            return FasterWhisperSTT(**kwargs)
        if provider == "indic":
            return IndicConformerSTT(**kwargs)
        elif provider == "deepgram":
            return DeepgramSTT(**kwargs)
        else:
            raise ValueError(f"Unknown STT provider: {provider}")
    
    @staticmethod
    def create_llm(
        provider: str,
        **kwargs
    ) -> LLMProvider:
        """
        Create LLM provider.
        
        Args:
            provider: "openai" 
            **kwargs: Provider-specific arguments
        """
        if provider == "openai":
            return OpenAILLM(**kwargs)
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
    
    @staticmethod
    def create_tts(
        provider: str,
        **kwargs
    ) -> TTSProvider:
        """
        Create TTS provider.
        
        Args:
            provider: "local" (Piper) or "cartesia"
            **kwargs: Provider-specific arguments
        """
        if provider == "piper":
            return PiperTTS(**kwargs)
        elif provider == "azure":
            return AzureTTS(**kwargs)
        elif provider == "cartesia":
            return CartesiaTTS(**kwargs)
        elif provider == "openai":
            return OpenAITTS(**kwargs)
        elif provider == "pyttsx3":
            return EspeakTTS(**kwargs)
        elif provider == "edge":
            return EdgeTTS(**kwargs)
        elif provider == "coqui":
            return CoquiTTS(**kwargs)
        else:
            raise ValueError(f"Unknown TTS provider: {provider}")
