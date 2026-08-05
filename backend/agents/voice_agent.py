"""Voice Agent - Converts Bangla text to speech using TTS providers."""

import os
from typing import Any

from agents.base import BaseAgent
from core.config.settings import get_settings
from utils.logger import get_logger

settings = get_settings()
logger = get_logger()


class VoiceAgent(BaseAgent):
    """Generates natural Bangla female voice from text."""

    async def execute(self, **kwargs) -> dict[str, Any]:
        text = kwargs.get("text", "")
        output_path = kwargs.get("output_path", "storage/audio/output.mp3")
        voice_name = kwargs.get("voice_name", settings.VOICE_NAME)
        provider = kwargs.get("provider", settings.DEFAULT_TTS_PROVIDER)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        logger.info(f"VoiceAgent: Generating voice using {provider}")

        try:
            if provider == "google":
                return await self._google_tts(text, output_path, voice_name)
            elif provider == "elevenlabs":
                return await self._elevenlabs_tts(text, output_path)
            elif provider == "azure":
                return await self._azure_tts(text, output_path, voice_name)
            else:
                return await self._google_tts(text, output_path, voice_name)
        except Exception as e:
            logger.error(f"VoiceAgent: TTS failed: {e}")
            return {"success": False, "error": str(e), "path": None}

    async def _google_tts(self, text: str, output_path: str, voice_name: str) -> dict:
        from google.cloud import texttospeech

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

        logger.info(f"VoiceAgent: ElevenLabs TTS saved to {output_path}")
        return {"success": True, "path": output_path, "provider": "elevenlabs"}

    async def _azure_tts(self, text: str, output_path: str, voice_name: str) -> dict:
        import azure.cognitiveservices.speech as speechsdk

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
        else:
            raise Exception(f"Azure TTS failed: {result.reason}")
