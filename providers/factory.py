"""Provider factory for easy instantiation."""
import os
from typing import Optional
from .base import STTProvider, LLMProvider, TTSProvider


class ProviderFactory:
    """Factory for creating provider instances."""
    
    @staticmethod
    def create_stt(
        provider: str = "local",
        **kwargs
    ) -> STTProvider:
        """
        Create STT provider.
        
        Args:
            provider: "local" (Faster Whisper) or "deepgram"
            **kwargs: Provider-specific arguments
        """
        if provider == "local":
            from .stt_local import FasterWhisperSTT
            return FasterWhisperSTT(**kwargs)
        if provider == "indic":
            from .stt_indic_conformer import IndicConformerSTT
            return IndicConformerSTT(**kwargs)
        elif provider == "deepgram":
            from .stt_deepgram import DeepgramSTT
            api_key = kwargs.pop("api_key", os.getenv("DEEPGRAM_API_KEY"))
            return DeepgramSTT(api_key=api_key, **kwargs)
        else:
            raise ValueError(f"Unknown STT provider: {provider}")
    
    @staticmethod
    def create_llm(
        provider: str = "openai",
        **kwargs
    ) -> LLMProvider:
        """
        Create LLM provider.
        
        Args:
            provider: "openai" (currently only option)
            **kwargs: Provider-specific arguments
        """
        if provider == "openai":
            from .llm_openai import OpenAILLM
            api_key = kwargs.pop("api_key", os.getenv("OPENAI_API_KEY"))
            return OpenAILLM(api_key=api_key, **kwargs)
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
    
    @staticmethod
    def create_tts(
        provider: str = "local",
        **kwargs
    ) -> TTSProvider:
        """
        Create TTS provider.
        
        Args:
            provider: "local" (Piper) or "cartesia"
            **kwargs: Provider-specific arguments
        """
        if provider == "local":
            from .tts_local import PiperTTS
            return PiperTTS(**kwargs)
        elif provider == "cartesia":
            from .tts_cartesia import CartesiaTTS
            api_key = kwargs.pop("api_key", os.getenv("CARTESIA_API_KEY"))
            return CartesiaTTS(api_key=api_key, **kwargs)
        elif provider == "openai":
            from .tts_openai import OpenAITTS
            api_key = kwargs.pop("api_key", os.getenv("OPENAI_API_KEY"))
            return OpenAITTS(api_key=api_key, **kwargs)
        elif provider == "pyttsx3":
            from .tts_espeak import EspeakTTS
            return EspeakTTS(**kwargs)
        elif provider == "edge":
            from .tts_edge import EdgeTTS
            return EdgeTTS(**kwargs)
        elif provider == "coqui":
            from .tts_coqui import CoquiTTS
            return CoquiTTS(**kwargs)
        else:
            raise ValueError(f"Unknown TTS provider: {provider}")
