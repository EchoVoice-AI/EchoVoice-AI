# backend/services/media.py

"""
Media-related services for EchoVoice AI.

Supports:
- Speech-to-Text (STT) using Azure Speech (real when configured, stub fallback)
- Text-to-Speech (TTS) using Azure Speech (real when configured, stub fallback)
- Translation using Azure Translator (real)
"""

from __future__ import annotations

import asyncio
import uuid
from pathlib import Path
from typing import Optional, Any

import httpx

# Azure SDK (TTS/STT)
import azure.cognitiveservices.speech as speechsdk  # type: ignore

from app import config
from services.logger import get_logger


logger = get_logger("media")


TTS_DIR = Path("data/tts")
TTS_DIR.mkdir(exist_ok=True, parents=True)

STT_TMP = Path("data/stt_tmp")
STT_TMP.mkdir(exist_ok=True, parents=True)


# ---------------------------------------------------------
# Helper: Check whether Azure Speech is configured
# ---------------------------------------------------------

def _has_speech_config() -> bool:
    return bool(config.AZURE_SPEECH_KEY and config.AZURE_SPEECH_REGION)


def _get_speech_config() -> speechsdk.SpeechConfig:
    if not _has_speech_config():
        raise RuntimeError("Azure Speech config missing")

    return speechsdk.SpeechConfig(
        subscription=config.AZURE_SPEECH_KEY,
        region=config.AZURE_SPEECH_REGION,
    )


# ---------------------------------------------------------
# SPEECH TO TEXT
# ---------------------------------------------------------

async def speech_to_text_from_url(audio_url: str) -> str:
    """
    Speech-to-text:
    - If Azure Speech configured → real STT
    - Else → stub fallback (local dev)
    """

    # Fallback: no Azure config
    if not _has_speech_config():
        logger.info("STT fallback mode — no Azure config set")
        return f"[STT stub transcript for {audio_url}]"

    # Real Azure path
    logger.info("Downloading audio from %s for STT", audio_url)

    tmp_path = STT_TMP / f"{uuid.uuid4().hex}.wav"

    async with httpx.AsyncClient() as client:
        r = await client.get(audio_url)
        r.raise_for_status()
        tmp_path.write_bytes(r.content)

    text = await asyncio.get_event_loop().run_in_executor(
        None, _stt_local_file, tmp_path
    )

    try:
        tmp_path.unlink(missing_ok=True)
    except:
        pass

    return text


def _stt_local_file(path: Path) -> str:
    speech_config = _get_speech_config()
    audio_config = speechsdk.AudioConfig(filename=str(path))
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config,
    )

    result = recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text

    raise RuntimeError(f"Azure STT failed — reason={result.reason}")


# ---------------------------------------------------------
# TEXT TO SPEECH
# ---------------------------------------------------------

async def text_to_speech_to_url(text: str) -> str:
    """
    Text-to-speech:
    - Real Azure TTS when configured
    - Stub fallback when missing
    """

    # Fallback
    if not _has_speech_config():
        logger.info("TTS fallback mode — no Azure config set")
        fake_url = "data/tts/fake-audio.wav"
        return fake_url

    # Real Azure TTS
    out_path = await asyncio.get_event_loop().run_in_executor(
        None, _tts_local_file, text
    )
    return str(out_path)


def _tts_local_file(text: str) -> Path:
    speech_config = _get_speech_config()
    speech_config.speech_synthesis_voice_name = (
        config.AZURE_SPEECH_TTS_VOICE or "en-US-JennyNeural"
    )

    filename = TTS_DIR / f"{uuid.uuid4().hex}.wav"

    audio_cfg = speechsdk.audio.AudioOutputConfig(filename=str(filename))
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_cfg
    )

    result = synthesizer.speak_text_async(text).get()

    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        raise RuntimeError(f"Azure TTS failed — reason={result.reason}")

    return filename


# ---------------------------------------------------------
# TRANSLATION (REAL ONLY)
# ---------------------------------------------------------

def _require_translator():
    if not config.AZURE_TRANSLATOR_KEY or not config.AZURE_TRANSLATOR_ENDPOINT:
        raise RuntimeError(
            "Azure Translator missing. "
            "Set AZURE_TRANSLATOR_KEY + AZURE_TRANSLATOR_ENDPOINT"
        )


async def translate_text(text: str, target_lang: str) -> str:
    _require_translator()

    endpoint = config.AZURE_TRANSLATOR_ENDPOINT.rstrip("/")
    url = f"{endpoint}/translate"

    params = {"api-version": "3.0", "to": target_lang}
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": config.AZURE_TRANSLATOR_KEY,
        "Ocp-Apim-Subscription-Region": config.AZURE_TRANSLATOR_REGION or "",
    }

    body = [{"Text": text}]

    logger.info("Calling Azure Translator → %s", target_lang)

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, params=params, headers=headers, json=body)

    resp.raise_for_status()
    data = resp.json()

    translated = data[0]["translations"][0]["text"]
    return translated
