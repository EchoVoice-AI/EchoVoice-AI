import os
import importlib
import json
from pathlib import Path


def _runs_dir():
    base = Path(__file__).resolve().parents[1]
    return base / ".langsmith_local_runs"


def test_monitor_noop_by_default():
    # Ensure env vars are unset
    os.environ.pop("LANGSMITH_ENABLED", None)
    os.environ.pop("LANGSMITH_API_KEY", None)

    import services.langsmith_monitor as monitor
    importlib.reload(monitor)

    assert monitor.LANGSMITH_ENABLED is False


def test_monitor_writes_local_file_when_enabled(tmp_path):
    # Enable monitoring via env var
    os.environ["LANGSMITH_ENABLED"] = "1"
    os.environ.pop("LANGSMITH_API_KEY", None)

    import services.langsmith_monitor as monitor
    importlib.reload(monitor)

    assert monitor.LANGSMITH_ENABLED is True

    runs_dir = _runs_dir()
    # Clean up any existing files
    if runs_dir.exists():
        for f in runs_dir.glob("*.json"):
            f.unlink()

    run_id = monitor.start_run("test.run", {"x": 1})
    # A file should be created for the run
    path = runs_dir / f"{run_id}.json"
    assert path.exists()

    # Log an event and finish
    monitor.log_event(run_id, "ev", {"k": "v"})
    monitor.finish_run(run_id, status="success", outputs={"ok": True})

    # Load and inspect
    with path.open("r", encoding="utf-8") as f:
        rec = json.load(f)

    assert rec.get("id") == run_id
    assert any(e.get("name") == "ev" for e in rec.get("events", []))
    assert rec.get("status") == "success"

    # cleanup
    path.unlink()
    os.environ.pop("LANGSMITH_ENABLED", None)


def test_segmenter_integration_creates_run(tmp_path):
    # Enable monitoring
    os.environ["LANGSMITH_ENABLED"] = "1"

    # Ensure clean runs dir
    runs_dir = _runs_dir()
    if runs_dir.exists():
        for f in runs_dir.glob("*.json"):
            f.unlink()

    # Run the segmenter which should create a run file
    from agents.segmenter import segment_user

    seg = segment_user({"user_id": "U123", "viewed_page": "payment_plans"})
    assert "segment" in seg

    files = list(runs_dir.glob("*.json"))
    assert files, "Expected at least one run file from segmenter"

    # cleanup
    for f in files:
        f.unlink()
    os.environ.pop("LANGSMITH_ENABLED", None)
