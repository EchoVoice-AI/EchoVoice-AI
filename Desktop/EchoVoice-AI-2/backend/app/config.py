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

# Environment (development|production)
ENV = os.getenv("ENV", os.getenv("APP_ENV", "development")).lower()

# CORS origins: allow explicit env var or sensible defaults in development
_env_origins = os.getenv("ALLOWED_ORIGINS")
if _env_origins:
	ALLOWED_ORIGINS: List[str] = [o.strip() for o in _env_origins.split(",") if o.strip()]
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
