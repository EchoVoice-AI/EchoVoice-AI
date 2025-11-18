from fastapi.testclient import TestClient
from app.main import app
from app.store import store


def test_orchestrator_persists_transient_state():
    """Call POST /orchestrate and assert transient keys were stored.

    The orchestrator stores transient values under keys of the form
    "{customer_id_or_email}:segment", ":citations", ":variants",
    ":analysis" and optionally ":winner". This test verifies those
    keys are present after a successful orchestration run.
    """

    client = TestClient(app)
    payload = {"customer": {"id": "test-123", "email": "test@example.com", "name": "Test User"}}

    resp = client.post("/orchestrate", json=payload)
    assert resp.status_code == 200, resp.text

    key_base = "test-123"

    # Check that orchestrator stored transient state
    segment = store.get(f"{key_base}:segment")
    citations = store.get(f"{key_base}:citations")
    variants = store.get(f"{key_base}:variants")
    analysis = store.get(f"{key_base}:analysis")

    assert segment is not None, "segment should be stored"
    assert citations is not None, "citations should be stored"
    assert variants is not None, "variants should be stored"
    assert analysis is not None, "analysis should be stored"

    # If a winner was chosen, it should also be stored
    winner = store.get(f"{key_base}:winner")
    if winner is not None:
        assert store.get(f"{key_base}:winner") == winner

    # Clean up keys after assertion to avoid test pollution
    store.delete(f"{key_base}:segment")
    store.delete(f"{key_base}:citations")
    store.delete(f"{key_base}:variants")
    store.delete(f"{key_base}:analysis")
    store.delete(f"{key_base}:winner")
