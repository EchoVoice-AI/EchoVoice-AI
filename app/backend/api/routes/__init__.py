"""API routes package. Aggregates smaller route modules into a single router."""
from fastapi import APIRouter

router = APIRouter()

# Import submodules so they register routers below
from . import health, ask_chat, uploads, content, chat_history, auth_setup, segmentation, generation, experimentation, retrieval  # noqa: F401

# Include sub-routers
router.include_router(health.router)
router.include_router(ask_chat.router)
router.include_router(uploads.router)
router.include_router(content.router)
router.include_router(chat_history.router)
router.include_router(auth_setup.router)
router.include_router(segmentation.router)
router.include_router(generation.router)
router.include_router(experimentation.router)
router.include_router(retrieval.router)