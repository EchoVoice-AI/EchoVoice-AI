"""Main FastAPI application setup."""
from fastapi import FastAPI

# from fastapi.staticfiles import StaticFiles
from .routes import router as api_router
from .startup import register as register_startup

app = FastAPI()

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
