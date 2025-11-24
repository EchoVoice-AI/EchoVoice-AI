# backend/services/media.py

"""
Media-related services for EchoVoice AI.

Responsibilities:
- Speech-to-Text (STT) using Azure Speech (planned)
- Text-to-Speech (TTS) using Azure Speech (planned)
- Translation using Azure Translator (implemented via REST)

These functions are pure service logic. Routers call these,
and they can later be re-used by other flows (e.g., LangGraph)
without going through HTTP again.
"""

from typing import Optional

import httpx

from app import config
from services.logger import get_logger

logger = get_logger("media")


class MediaConfigError(RuntimeError):
    """Raised when required Azure media configuration is missing."""


def _require_speech_config() -> None:
    """Ensure Azure Speech configuration is set before STT/TTS calls."""
    if not config.AZURE_SPEECH_KEY or not config.AZURE_SPEECH_REGION:
        raise MediaConfigError(
            "Azure Speech config missing. "
            "Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION in your environment."
        )


def _require_translator_config() -> None:
    """Ensure Azure Translator configuration is set before translation calls."""
    if not config.AZURE_TRANSLATOR_KEY or not config.AZURE_TRANSLATOR_ENDPOINT:
        raise MediaConfigError(
            "Azure Translator config missing. "
            "Set AZURE_TRANSLATOR_KEY and AZURE_TRANSLATOR_ENDPOINT "
            "in your environment."
        )


# --------- Speech to Text --------- #

async def speech_to_text_from_url(audio_url: str) -> str:
    """
    Convert speech (from an audio URL) into text.

    Current implementation is a stub for local development:
    - Validates that Azure Speech config is present.
    - Logs the call.
    - Returns a placeholder transcript.

    Later, you can replace the stub with a real Azure Speech SDK or REST call.
    """
    _require_speech_config()
    logger.info("Starting speech-to-text for audio_url=%s", audio_url)

    # TODO: Replace this stub with a real Azure Speech call.
    transcript = f"[stub transcript for {audio_url}]"

    logger.info("Completed speech-to-text for audio_url=%s", audio_url)
    return transcript


# --------- Text to Speech --------- #

async def text_to_speech_to_url(text: str) -> str:
    """
    Convert text into speech and return an audio URL.

    Current implementation is a stub:
    - Validates Azure Speech config.
    - Logs the call.
    - Returns a fake URL.

    In a real implementation you would:
    - Call Azure TTS to generate audio.
    - Store the audio in blob storage (or similar).
    - Return the storage URL for the UI to play.
    """
    _require_speech_config()
    logger.info("Starting text-to-speech (text length=%d)", len(text))

    # TODO: Replace this stub with a real Azure TTS call and persisted audio.
    fake_audio_url = "https://example.com/audio/generated-from-tts.wav"

    logger.info("Completed text-to-speech, audio_url=%s", fake_audio_url)
    return fake_audio_url


# --------- Translation --------- #

async def translate_text(text: str, target_lang: str) -> str:
    """
    Translate text using Azure Translator REST API.

    Uses:
    - AZURE_TRANSLATOR_ENDPOINT (e.g. "https://api.cognitive.microsofttranslator.com")
    - AZURE_TRANSLATOR_KEY
    - AZURE_TRANSLATOR_REGION (if required by your resource)
    """
    _require_translator_config()
    logger.info(
        "Starting translation to target_lang=%s (text length=%d)",
        target_lang,
        len(text),
    )

    base = config.AZURE_TRANSLATOR_ENDPOINT.rstrip("/")
    url = f"{base}/translate"

    params = {
        "api-version": "3.0",
        "to": target_lang,
    }

    headers = {
        "Ocp-Apim-Subscription-Key": config.AZURE_TRANSLATOR_KEY,
        # Some Azure setups require the region header as well.
        "Ocp-Apim-Subscription-Region": config.AZURE_TRANSLATOR_REGION or "",
        "Content-Type": "application/json",
    }

    body = [{"Text": text}]

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, params=params, headers=headers, json=body)
        resp.raise_for_status()
    except httpx.HTTPError as e:
        logger.exception("Azure Translator HTTP error")
        raise RuntimeError("Azure Translator request failed") from e

    try:
        data = resp.json()
        # Expected response shape:
        # [
        #   {
        #     "translations": [
        #       {
        #         "text": "...",
        #         "to": "xx"
        #       }
        #     ]
        #   }
        # ]
        first_item = data[0]
        translations = first_item.get("translations", [])
        if not translations:
            raise KeyError("Missing 'translations' in Azure response")
        translated_text = translations[0]["text"]
    except Exception as e:
        logger.exception("Failed to parse Azure Translator response")
        raise RuntimeError("Invalid response from Azure Translator") from e

    logger.info("Completed translation to target_lang=%s", target_lang)
    return translated_text
