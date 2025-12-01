"""Main FastAPI application setup."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
from .routes import router as api_router
from .startup import register as register_startup

app = FastAPI(
    title="EchoVoice AI Orchestrator",
    description="Backend API for Multi-Agent Marketing Personalization",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8082"],  # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (serves the same static folder used by the Quart blueprint)
# app.mount("/static", StaticFiles(directory="./static"), name="static")

# Include API routes
app.include_router(api_router)

# Register startup/shutdown handlers
register_startup(app)

# Minimal root route to serve index (frontend expects `/`)
@app.get("/")
async def index():
    """Serve a minimal index response."""
    return {"status": "EchoVoice FastAPI migration - index served by static files at /static"}
