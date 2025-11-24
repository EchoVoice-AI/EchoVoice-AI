# backend/app/config.py

import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

# API keys / external endpoints
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
VECTOR_DB_ENDPOINT = os.getenv('VECTOR_DB_ENDPOINT')
VECTOR_DB_API_KEY = os.getenv('VECTOR_DB_API_KEY')
DELIVERY_PROVIDER_API_KEY = os.getenv('DELIVERY_PROVIDER_API_KEY')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Azure OpenAI (for embeddings + chat)
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv(
    "AZURE_OPENAI_API_VERSION",
    "2024-02-15-preview",
)

# Embeddings deployment (to use this in vector_db)
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT = os.getenv(
    "AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT"
)

# Chat deployment name for generator
AZURE_OPENAI_CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")

# === NEW: Azure Speech + Translator config for media services ===
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")

AZURE_TRANSLATOR_KEY = os.getenv("AZURE_TRANSLATOR_KEY")
AZURE_TRANSLATOR_REGION = os.getenv("AZURE_TRANSLATOR_REGION")
AZURE_TRANSLATOR_ENDPOINT = os.getenv("AZURE_TRANSLATOR_ENDPOINT")
# e.g. "https://api.cognitive.microsofttranslator.com"

# Optional: non-Azure OpenAI fallback
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")

# Environment (development|production)
ENV = os.getenv("ENV", os.getenv("APP_ENV", "development")).lower()

# CORS origins: allow explicit env var or sensible defaults in development
_env_origins = os.getenv("ALLOWED_ORIGINS")
if _env_origins:
    ALLOWED_ORIGINS: List[str] = [
        o.strip() for o in _env_origins.split(",") if o.strip()
    ]
else:
    if ENV == "production":
        # In production default to an explicit, empty list to force operators to opt-in.
        prod_origin = os.getenv("PRODUCTION_ORIGIN")
        ALLOWED_ORIGINS = [prod_origin] if prod_origin else []
    else:
        # Development-friendly defaults
        ALLOWED_ORIGINS = [
            "http://localhost",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
        ]


def get_allowed_origins() -> List[str]:
    """Return the configured origins list."""
    return ALLOWED_ORIGINS


# Redis URL for adapter (optional - set to enable Redis-backed store)
REDIS_URL = os.getenv("REDIS_URL")


def is_debug_enabled() -> bool:
	"""Return True when debug routes/features should be enabled.

	Controlled via the `ECHO_DEBUG` environment variable (1/true/yes).
	"""
	val = os.getenv("ECHO_DEBUG", "").lower()
	return val in ("1", "true", "yes")
