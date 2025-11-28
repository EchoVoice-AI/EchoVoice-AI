import pytest
from fastapi.testclient import TestClient


def test_ask_route_injects_mock_approach(monkeypatch):
    # Import app and dependency helpers
    from api.main import app as fastapi_app
    from api.dependencies import get_ask_approach, get_auth_claims

    # Create a mock approach with an async run method
    class MockApproach:
        async def run(self, messages, context=None, session_state=None):
            return {
                "message": {"content": "mocked reply", "role": "assistant"},
                "context": {},
                "session_state": session_state,
            }

    mock_approach = MockApproach()

    # Override dependencies: approach and auth claims
    fastapi_app.dependency_overrides[get_ask_approach] = lambda: mock_approach
    fastapi_app.dependency_overrides[get_auth_claims] = lambda: {}

    with TestClient(fastapi_app) as client:
        payload = {"messages": [{"role": "user", "content": "hello"}]}
        resp = client.post("/ask", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["message"]["content"] == "mocked reply"
