import asyncio
import azure.cognitiveservices.speech as speechsdk
from .base import TTSProvider


class AzureTTS(TTSProvider):
    def __init__(
        self,
        speech_key: str,
        region: str,
        voice: str = "hi-IN-SwaraNeural",
        sample_rate: int = 16000,
    ):
        self.speech_config = speechsdk.SpeechConfig(
            subscription=speech_key,
            region=region
        )

        self.speech_config.speech_synthesis_voice_name = voice

        # IMPORTANT: force WAV RIFF output
        self.speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm
        )

        # 👇 NO speaker, NO stream
        self.audio_config = None

        self.sample_rate = sample_rate

    async def synthesize(self, text: str) -> bytes:
        loop = asyncio.get_running_loop()

        def _run():
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=self.audio_config
            )

            result = synthesizer.speak_text(text)

            if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
                raise RuntimeError(f"Azure TTS failed: {result.reason}")

            # 🔑 THIS IS THE KEY LINE
            audio = result.audio_data

            print(f"🔊 [AzureTTS] bytes={len(audio)} header={audio[:12]}")

            return audio

        return await loop.run_in_executor(None, _run)

    def get_audio_format(self) -> dict:
        return {
            "format": "wav",
            "sample_rate": self.sample_rate,
            "channels": 1,
            "encoding": "pcm16"
        }
