from fastapi.testclient import TestClient
from app.main import app
from app.routers.orchestrator import get_segmenter
from app.store import store


class FakeSegmenter:
    def run(self, customer):
        return {"segment": "fake-seg"}


def test_override_segmenter_and_persist():
    # Override the segmenter provider so orchestrator uses our fake
    app.dependency_overrides[get_segmenter] = lambda: FakeSegmenter()
    client = TestClient(app)
    resp = client.post("/orchestrate", json={"customer": {"id": "node-1", "email": "n@example.com"}})
    assert resp.status_code == 200

    # segment should have been stored by the orchestrator
    seg = store.get("node-1:segment")
    assert seg == {"segment": "fake-seg"}

    # cleanup
    store.delete("node-1:segment")
    store.delete("node-1:citations")
    store.delete("node-1:variants")
    store.delete("node-1:analysis")
    store.delete("node-1:winner")
    app.dependency_overrides.clear()
