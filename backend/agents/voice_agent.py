"""Voice Agent - Converts Bangla text to speech using TTS providers."""

import asyncio
import os
from typing import Any

from agents.base import BaseAgent
from core.config.settings import get_settings
from utils.logger import get_logger

settings = get_settings()
logger = get_logger()


class VoiceAgent(BaseAgent):
    """Generates natural Bangla female voice from text with automatic provider fallback."""

    async def execute(self, **kwargs) -> dict[str, Any]:
        text = kwargs.get("text", "")
        output_path = kwargs.get("output_path", "storage/audio/output.mp3")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Try providers in order: gTTS (free) → Google Cloud → ElevenLabs → Azure
        providers = [
            ("gtts", self._gtts),
        ]
        if settings.GOOGLE_API_KEY or os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            providers.append(("google", self._google_tts))
        if settings.ELEVENLABS_API_KEY:
            providers.append(("elevenlabs", self._elevenlabs_tts))
        if settings.AZURE_SPEECH_KEY:
            providers.append(("azure", self._azure_tts))

        for name, method in providers:
            try:
                logger.info(f"VoiceAgent: Trying {name} TTS...")
                print(f"  Generating voice with {name}...", flush=True)
                result = await method(text, output_path)
                if result.get("success"):
                    return result
            except Exception as e:
                logger.warning(f"VoiceAgent: {name} TTS failed: {e}")
                print(f"  {name} failed: {e}", flush=True)

        logger.error("VoiceAgent: All TTS providers failed")
        return {"success": False, "error": "All TTS providers failed", "path": None}

    async def _gtts(self, text: str, output_path: str) -> dict:
        from gtts import gTTS as GTTS

        tts = GTTS(text=text, lang="bn", slow=False)
        await asyncio.to_thread(tts.save, output_path)
        logger.info(f"VoiceAgent: gTTS saved to {output_path}")
        return {"success": True, "path": output_path, "provider": "gtts"}

    async def _google_tts(self, text: str, output_path: str) -> dict:
        from google.cloud import texttospeech

        voice_name = settings.VOICE_NAME or "bn-IN-Wavenet-A"
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="bn-IN",
            name=voice_name,
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,
            pitch=0.0,
        )
        response = await client.synthesize_speech_async(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        with open(output_path, "wb") as f:
            f.write(response.audio_content)
        logger.info(f"VoiceAgent: Google TTS saved to {output_path}")
        return {"success": True, "path": output_path, "provider": "google"}

    async def _elevenlabs_tts(self, text: str, output_path: str) -> dict:
        from elevenlabs import generate, save, set_api_key

        set_api_key(settings.ELEVENLABS_API_KEY)
        audio = generate(text=text, voice="Rachel", model="eleven_multilingual_v2")
        save(audio, output_path)
        logger.info(f"VoiceAgent: ElevenLabs saved to {output_path}")
        return {"success": True, "path": output_path, "provider": "elevenlabs"}

    async def _azure_tts(self, text: str, output_path: str) -> dict:
        import azure.cognitiveservices.speech as speechsdk

        voice_name = settings.VOICE_NAME or "bn-IN-Wavenet-A"
        speech_config = speechsdk.SpeechConfig(
            subscription=settings.AZURE_SPEECH_KEY,
            region=settings.AZURE_SPEECH_REGION,
        )
        speech_config.speech_synthesis_voice_name = voice_name
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config, audio_config=audio_config
        )
        result = synthesizer.speak_text_async(text).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logger.info(f"VoiceAgent: Azure TTS saved to {output_path}")
            return {"success": True, "path": output_path, "provider": "azure"}
        raise Exception(f"Azure TTS failed: {result.reason}")
