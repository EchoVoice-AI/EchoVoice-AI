import asyncio
import importlib
import os
import sys
from pathlib import Path

import pytest


def _ensure_backend_on_path():
    # Ensure tests run with backend/ on sys.path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


@pytest.mark.asyncio
async def test_dispatcher_with_sqlite(tmp_path, monkeypatch):
    """Integration test: use a temporary SQLite DB to validate dispatcher behavior.

    This test sets `DATABASE_URL` to a tmp sqlite file, imports the real
    `api.db` module to create tables, wires it into `api.storage`, then
    stubs `run_graph` to simulate quick runs and validates queued -> running
    transitions.
    """
    _ensure_backend_on_path()

    db_file = tmp_path / "test_dispatcher.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_file}"

    # Insert a lightweight package module to avoid executing `api.__init__`
    import types

    pkg = types.ModuleType("api")
    pkg.__path__ = [str(Path(__file__).resolve().parents[2] / "api")]
    sys.modules["api"] = pkg

    # Import and reload DB module so engine is created from our env var
    import api.db as db
    importlib.reload(db)
    # create tables
    db.create_db_and_tables()

    # Wire into storage
    import api.storage as storage

    importlib.reload(storage)
    storage.USE_DB = True
    storage._db = db

    # Import runner and ensure it's using our storage._db
    import importlib as _imp

    runner = _imp.import_module("api.runner")
    _imp.reload(runner)
    runner.storage.USE_DB = True
    runner.storage._db = db

    # Reduce concurrency to 1 for deterministic behavior
    monkeypatch.setattr(runner.SETTINGS, "MAX_CONCURRENT_RUNS", 1)

    # stub run_graph to mark run finished quickly using the real DB helpers
    async def _stub_run_graph(initial_state, run_id=None):
        await asyncio.sleep(0.02)
        # mark finished in DB
        db.set_run_result(run_id, {"ok": True})
        db.update_run_status(run_id, "finished")
        # call dispatcher so queued runs are started
        runner._maybe_start_queued_runs()
        return {"ok": True}

    monkeypatch.setattr(runner, "run_graph", _stub_run_graph)

    # Start first run -> should become running immediately
    rid1 = runner.start_async_run({"input": 1}, run_id="i-run-1")
    # Start second run -> should be queued due to max_concurrent_runs=1
    rid2 = runner.start_async_run({"input": 2}, run_id="i-run-2")

    # Validate DB recorded
    row1 = db.get_run(rid1)
    row2 = db.get_run(rid2)
    assert row1 is not None and row2 is not None
    assert row2["status"] == "queued"

    # Wait for dispatcher to promote queued run
    await asyncio.sleep(0.2)

    r2 = db.get_run(rid2)
    assert r2["status"] in ("running", "finished")

    # cleanup scheduled tasks
    for t in list(runner.RUN_TASKS.values()):
        try:
            await t
        except Exception:
            pass
