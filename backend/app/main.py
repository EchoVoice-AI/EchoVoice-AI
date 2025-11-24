from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_allowed_origins, is_debug_enabled
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn

from backend.services.logger import get_logger
from .routers.health import router as health_router
from .routers.orchestrator import router as orchestrator_router
from .routers.media import router as media_router # added import for media router

logger = get_logger('orchestrator')
app = FastAPI(title='EchoVoice-AI Orchestrator')

# CORS middleware (configured via `backend.config`)
origins = get_allowed_origins()

# If running in production with no origins configured, be conservative.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers (standard `routers/` package)
app.include_router(health_router)
app.include_router(orchestrator_router)
app.include_router(media_router)  # included media router

# Mount debug router only when explicitly enabled in environment (dev only)
if is_debug_enabled():
    app.include_router(debug_router)



if __name__ == '__main__':
    # Run with Uvicorn for development
    uvicorn.run(app, host='127.0.0.1', port=8000)
