# backend/app/routers/media.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services import media as media_service  # our service layer with Azure / logic

router = APIRouter(
    prefix="/media",
    tags=["media"],
)


# --------- Speech to Text --------- #

class STTRequest(BaseModel):
    """Request body for Speech-to-Text."""
    # For now we accept a URL pointing to an audio file.
    # Later you can add support for file uploads or base64 if needed.
    audio_url: str


class STTResponse(BaseModel):
    """Response body for Speech-to-Text."""
    text: str


@router.post("/speech-to-text", response_model=STTResponse)
async def speech_to_text(payload: STTRequest) -> STTResponse:
    """
    Convert speech (audio file at a URL) into text.

    This is meant to support UI flows where a human reviewer dictates content
    or needs an audio recording transcribed.
    """
    try:
        text = await media_service.speech_to_text_from_url(payload.audio_url)
        return STTResponse(text=text)
    except Exception as e:
        # In production you might log more detail but return a generic message.
        raise HTTPException(status_code=500, detail="Speech-to-text failed") from e


# --------- Text to Speech --------- #

class TTSRequest(BaseModel):
    """Request body for Text-to-Speech."""
    # The email text (or part of it) that should be read out loud.
    text: str


class TTSResponse(BaseModel):
    """Response body for Text-to-Speech."""
    # URL where the generated audio can be fetched/streamed by the UI.
    audio_url: str


@router.post("/text-to-speech", response_model=TTSResponse)
async def text_to_speech(payload: TTSRequest) -> TTSResponse:
    """
    Convert text into speech and return an audio URL.

    The UI can call this so the human reviewer can listen to the email
    instead of reading the text.
    """
    try:
        audio_url = await media_service.text_to_speech_to_url(payload.text)
        return TTSResponse(audio_url=audio_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Text-to-speech failed") from e


# --------- Translation --------- #

class TranslateRequest(BaseModel):
    """Request body for translation."""
    text: str
    target_lang: str  # e.g. "es", "fr", "ta"


class TranslateResponse(BaseModel):
    """Response body for translation."""
    translated_text: str


@router.post("/translate", response_model=TranslateResponse)
async def translate(payload: TranslateRequest) -> TranslateResponse:
    """
    Translate text into the target language.

    Used by the reviewer UI to see the generated email in different languages.
    """
    try:
        translated = await media_service.translate_text(
            payload.text,
            payload.target_lang,
        )
        return TranslateResponse(translated_text=translated)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Translation failed") from e
