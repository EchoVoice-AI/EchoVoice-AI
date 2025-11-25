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
# cleanup dependency overrides
    app.dependency_overrides.clear()

def test_debug_previews_mock():
    # ensure mock=true returns precomputed previews without depending on orchestration
    client = TestClient(app)
    r = client.get("/debug/deliveries?mock=true")
    assert r.status_code == 200
    data = r.json()
    assert "previews" in data
    # mock fixtures include U001 and U002 with subjects matching PRECOMPUTED_PREVIEWS
    assert any(p["user_id"] == "U001" and "running shoes" in (p.get("subject") or "") for p in data["previews"])
    assert any(p["user_id"] == "U002" and "Acme plan" in (p.get("subject") or "") for p in data["previews"])


def test_body_text_alias(monkeypatch):
    """Ensure each preview includes `body_text` equal to `body`."""
    app.dependency_overrides[get_orchestrator] = lambda: get_mock_orchestrator()
    client = TestClient(app)

    r = client.get("/debug/deliveries")
    assert r.status_code == 200
    data = r.json()
    assert "previews" in data
    for p in data["previews"]:
        # alias should be present and match body (both may be None)
        assert "body_text" in p
        assert p["body_text"] == p.get("body")
    app.dependency_overrides.clear()

def test_debug_previews_cache(monkeypatch):
    """When ECHO_DEBUG_CACHE_TTL is set, subsequent requests within TTL should not re-run orchestrator."""
    # small TTL for test
    os.environ["ECHO_DEBUG_CACHE_TTL"] = "60"

    class CounterOrchestrator:
        def __init__(self):
            self.count = 0

        async def run_flow(self, flow_name, payload):
            self.count += 1
            # return a simple deterministic safe variant
            return {
                "analysis": {"winner": {"variant_id": "A"}},
                "safety": {"safe": [{"id": "A", "subject": "S A", "body": "B A"}]},
            }

    counter = CounterOrchestrator()
    app.dependency_overrides[get_orchestrator] = lambda: counter
    client = TestClient(app)

    r1 = client.get("/debug/deliveries")
    assert r1.status_code == 200
    # after first request, orchestrator should have been invoked (once per customer)
    # our mock increments once per run_flow call; there are two mock customers => count == 2
    assert counter.count == 2

    # Second request within TTL should use cache and not increment counter
    r2 = client.get("/debug/deliveries")
    assert r2.status_code == 200
    assert counter.count == 2

    # cleanup env
    os.environ.pop("ECHO_DEBUG_CACHE_TTL", None)
    app.dependency_overrides.clear()


def test_debug_run_full_pipeline():
    """Test POST /debug/run returns full orchestrator result (MessageState)."""
    class FullMockOrchestrator:
        async def run_flow(self, flow_name, payload):
            # Return complete MessageState structure
            return {
                "segment": {"category": "high_value"},
                "citations": ["citation1", "citation2"],
                "variants": [
                    {"id": "V1", "subject": "Subject 1", "body": "Body 1"},
                    {"id": "V2", "subject": "Subject 2", "body": "Body 2"},
                ],
                "safety": {
                    "safe": [{"id": "V1", "subject": "Subject 1", "body": "Body 1"}],
                    "blocked": [{"id": "V2", "reason": "policy violation"}],
                },
                "analysis": {"winner": {"variant_id": "V1"}},
                "delivery": {"status": "sent", "message_id": "msg123"},
            }

    app.dependency_overrides[get_orchestrator] = lambda: FullMockOrchestrator()
    client = TestClient(app)

    payload = {
        "customer": {
            "id": "U999",
            "name": "Test User",
            "email": "test@example.com",
        }
    }

    r = client.post("/debug/run", json=payload)
    assert r.status_code == 200
    data = r.json()

    # Verify all expected keys are present in full MessageState
    assert "segment" in data
    assert "citations" in data
    assert "variants" in data
    assert "safety" in data
    assert "analysis" in data
    assert "delivery" in data

    # Verify some structure
    assert data["segment"]["category"] == "high_value"
    assert len(data["variants"]) == 2
    assert data["analysis"]["winner"]["variant_id"] == "V1"

    app.dependency_overrides.clear()
