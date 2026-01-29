"""
Example configurations for different use cases.
Copy the relevant configuration to server.py.
"""

# ============================================
# Example 1: Fully Local (No API keys needed)
# ============================================
FULLY_LOCAL = {
    "STT_CONFIG": {
        "provider": "local",
        "model_size": "base",
        "language": None,  # Auto-detect
        "device": "cpu",
        "compute_type": "int8",
    },
    "LLM_CONFIG": {
        "provider": "openai",  # Still needs OpenAI for LLM
        "model": "gpt-4o-mini",
    },
    "TTS_CONFIG": {
        "provider": "local",
        "model_path": "/path/to/en_US-lessac-medium.onnx",
    }
}

# ============================================
# Example 2: Fully Cloud (Low latency)
# ============================================
FULLY_CLOUD = {
    "STT_CONFIG": {
        "provider": "deepgram",
        "model": "nova-2",
        "language": "en",
    },
    "LLM_CONFIG": {
        "provider": "openai",
        "model": "gpt-4o-mini",
    },
    "TTS_CONFIG": {
        "provider": "cartesia",
        "voice_id": "a0e99841-438c-4a64-b679-ae501e7d6091",
        "model_id": "sonic-english",
    }
}

# ============================================
# Example 3: Hybrid (Local STT/TTS, Cloud LLM)
# ============================================
HYBRID = {
    "STT_CONFIG": {
        "provider": "local",
        "model_size": "small",  # Better accuracy
        "language": "en",
        "device": "cpu",
        "compute_type": "int8",
    },
    "LLM_CONFIG": {
        "provider": "openai",
        "model": "gpt-4o",  # More capable model
    },
    "TTS_CONFIG": {
        "provider": "local",
        "model_path": "/path/to/en_US-lessac-medium.onnx",
    }
}

# ============================================
# Example 4: Multilingual Spanish
# ============================================
SPANISH = {
    "STT_CONFIG": {
        "provider": "local",
        "model_size": "base",
        "language": "es",  # Spanish
        "device": "cpu",
        "compute_type": "int8",
    },
    "LLM_CONFIG": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "system_prompt": "Eres un asistente de voz útil. Mantén las respuestas concisas y conversacionales.",
    },
    "TTS_CONFIG": {
        "provider": "local",
        "model_path": "/path/to/es_ES-davefx-medium.onnx",  # Spanish voice
    }
}

# ============================================
# Example 5: High Accuracy (Slower)
# ============================================
HIGH_ACCURACY = {
    "STT_CONFIG": {
        "provider": "local",
        "model_size": "large-v3",  # Most accurate
        "language": None,
        "device": "cpu",
        "compute_type": "int8",
        "vad_filter": True,
    },
    "LLM_CONFIG": {
        "provider": "openai",
        "model": "gpt-4o",  # Most capable
    },
    "TTS_CONFIG": {
        "provider": "cartesia",
        "voice_id": "a0e99841-438c-4a64-b679-ae501e7d6091",
        "model_id": "sonic-english",
    }
}

# ============================================
# Example 6: Fast & Lightweight
# ============================================
FAST_LIGHTWEIGHT = {
    "STT_CONFIG": {
        "provider": "local",
        "model_size": "tiny",  # Fastest
        "language": "en",
        "device": "cpu",
        "compute_type": "int8",
    },
    "LLM_CONFIG": {
        "provider": "openai",
        "model": "gpt-4o-mini",
    },
    "TTS_CONFIG": {
        "provider": "local",
        "model_path": "/path/to/en_US-lessac-low.onnx",  # Low quality = faster
    }
}
