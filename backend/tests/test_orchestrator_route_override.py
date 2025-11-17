from fastapi.testclient import TestClient
from app.main import app
from app.routers.orchestrator import get_orchestrator


class FakeOrch:
    async def run_flow(self, flow_name, payload):
        return {"status": "ok", "flow": flow_name, "result": "fake-result"}


def test_orchestrator_route_uses_dependency_override():
    # Override the orchestrator dependency with a fake implementation
    app.dependency_overrides[get_orchestrator] = lambda: FakeOrch()
    client = TestClient(app)

    resp = client.post("/orchestrate", json={"customer": {"id": "x", "email": "x@example.com"}})
    assert resp.status_code == 200
    assert resp.json().get("result") == "fake-result"

    # Clear overrides to avoid affecting other tests
    app.dependency_overrides.clear()
