import importlib
import json
import sys
from pathlib import Path


def _reload_monitor(monkeypatch):
    # Ensure the monitor module picks up environment changes during tests
    monkeypatch.setenv("LANGSMITH_ENABLED", "1")
    # Remove module if already loaded so import picks up env changes
    if "backend.services.langsmith_monitor" in sys.modules:
        importlib.reload(sys.modules["backend.services.langsmith_monitor"])
    else:
        importlib.import_module("backend.services.langsmith_monitor")
    return sys.modules["backend.services.langsmith_monitor"]


def test_pseudonymization_with_secret(monkeypatch, tmp_path):
    monkeypatch.setenv("LANGSMITH_HMAC_SECRET", "test-secret-123")
    monitor = _reload_monitor(monkeypatch)

    run_id = monitor.start_run("segmenter.segment_user", metadata={
        "customer_id": "cust_002",
        "last_event": "payment_plans",
    })

    path = Path(monitor.RUNS_DIR) / f"{run_id}.json"
    assert path.exists(), "run file should be written"
    data = json.loads(path.read_text(encoding="utf-8"))

    # raw id must not be present
    assert "customer_id" not in data.get("metadata", {}), "raw customer_id must not be stored"
    assert "customer_id_hash" in data.get("metadata", {}), "hashed id must be present"
    ps = data["metadata"].get("pseudonymization", {})
    assert ps.get("method") == "hmac-sha256"
    assert ps.get("secret_present") is True


def test_pseudonymization_without_secret(monkeypatch):
    # Ensure no secret is set
    monkeypatch.delenv("LANGSMITH_HMAC_SECRET", raising=False)
    monitor = _reload_monitor(monkeypatch)

    run_id = monitor.start_run("segmenter.segment_user", metadata={"customer_id": "cust_003"})
    path = Path(monitor.RUNS_DIR) / f"{run_id}.json"
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))

    assert "customer_id" not in data.get("metadata", {})
    assert "customer_id_hash" in data.get("metadata", {})
    ps = data["metadata"].get("pseudonymization", {})
    assert ps.get("method") == "sha256"
    assert ps.get("secret_present") is False
