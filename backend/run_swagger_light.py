from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import uvicorn

try:
    # Reuse the project's CORS config when available
    from app.config import get_allowed_origins
    origins = get_allowed_origins()
except Exception:
    origins = ["http://localhost", "http://127.0.0.1:3000"]

app = FastAPI(title="EchoVoice-AI Orchestrator (light)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}


# Lightweight Pydantic models mirroring the real API so Swagger shows the schema
class CustomerModel(BaseModel):
    id: Optional[str] = Field(None, example="U001")
    name: Optional[str] = Field(None, example="Selvi")
    email: Optional[str] = Field(None, example="a@example.com")
    last_event: Optional[str] = Field(None, example="payment_plans")
    properties: Dict[str, Any] = Field(default_factory=dict)


class OrchestrateRequest(BaseModel):
    customer: CustomerModel


@app.post("/orchestrate")
async def orchestrate(payload: OrchestrateRequest):
    """Dummy orchestrate endpoint for local Swagger UI.

    This returns the parsed payload and does NOT call any heavy services.
    It's intended for local testing of the OpenAPI/Swagger UI only.
    """
    # Return a minimal response so the docs show request/response shapes
    return {"status": "ok", "received": payload.customer.model_dump()}


if __name__ == "__main__":
    uvicorn.run("run_swagger_light:app", host="127.0.0.1", port=8000)
