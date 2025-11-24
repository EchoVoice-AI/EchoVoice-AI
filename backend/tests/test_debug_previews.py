import os

# Enable debug router before importing app so the router is mounted
os.environ.setdefault("ECHO_DEBUG", "1")

from fastapi.testclient import TestClient
from app.main import app
from app.routers.orchestrator import get_orchestrator


class MockOrchestrator:
    async def run_flow(self, flow_name, payload):
        # deterministic results for tests based on id
        if payload.get("id") == "U001":
            return {
                "analysis": {"winner": {"variant_id": "A"}},
                "safety": {"safe": [{"id": "A", "subject": "S A", "body": "B A"}]},
            }
        if payload.get("id") == "U002":
            return {
                "analysis": {"winner": None},
                "safety": {"safe": [{"id": "B", "subject": "S B", "body": "B B"}]},
            }
        return {"analysis": {}, "safety": {"safe": []}}


def get_mock_orchestrator():
    return MockOrchestrator()


def test_debug_previews(monkeypatch):
    # Override the orchestrator dependency with our mock
    app.dependency_overrides[get_orchestrator] = lambda: get_mock_orchestrator()
    client = TestClient(app)

    r = client.get("/debug/deliveries")
    assert r.status_code == 200
    data = r.json()
    assert "previews" in data
    # check U001 used winner A
    assert any(p["user_id"] == "U001" and p["subject"] == "S A" for p in data["previews"])
    # check U002 used fallback to first safe variant
    assert any(p["user_id"] == "U002" and p["subject"] == "S B" for p in data["previews"])
