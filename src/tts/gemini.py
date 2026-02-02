import asyncio
from google import genai
from google.genai import types
from src.tts.tts_provider import TTSProvider

class GeminiTTS(TTSProvider):
    def __init__(
        self,
        api_key: str,
        voice: str = "Puck",  # Matches your JS: Puck, Charon, Kore, Fenrir, Aoede
        sample_rate: int = 24000, # Recommended for Gemini Audio
    ):
        # Use the new Unified SDK
        self.client = genai.Client(api_key=api_key)
        self.voice = voice
        self.sample_rate = sample_rate
        # USE THE EXACT MODEL FROM YOUR WORKING JS CODE
        self.model_id = "gemini-2.5-flash-preview-tts" 

    async def synthesize(self, text: str) -> bytes:
        loop = asyncio.get_running_loop()

        def _run():
            # Match the config structure from your JS code
            config = types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=self.voice
                        )
                    )
                )
            )

            try:
                # Standard generate_content call (not streaming)
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=text,
                    config=config
                )

                # Extract audio from the response candidates
                # Matches JS: response.candidates[0].content.parts[0].inlineData.data
                if response.candidates and response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        if part.inline_data:
                            audio_data = part.inline_data.data
                            print(f"🔊 [GeminiTTS] Success: {len(audio_data)} bytes")
                            return audio_data
                
                print("⚠️ [GeminiTTS] No audio data in response")
                return b""

            except Exception as e:
                print(f"❌ [GeminiTTS] API Error: {e}")
                return b""

        return await loop.run_in_executor(None, _run)

    def get_audio_format(self) -> dict:
        return {
            "format": "wav",
            "sample_rate": self.sample_rate,
            "channels": 1,
            "encoding": "pcm16",
        }