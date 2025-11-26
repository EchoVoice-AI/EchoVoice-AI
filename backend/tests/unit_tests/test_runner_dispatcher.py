import asyncio
import types

import sys
from pathlib import Path

import pytest

# Ensure the backend package directory is on sys.path when pytest runs.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Avoid importing `api.__init__` which constructs the FastAPI app; instead
# insert a lightweight package module pointing to the `api/` dir so we can
# import the `api.runner` submodule directly without triggering app startup.
import importlib

pkg = types.ModuleType("api")
pkg.__path__ = [str(Path(__file__).resolve().parents[2] / "api")]
sys.modules["api"] = pkg
runner = importlib.import_module("api.runner")


class FakeDB:
    def __init__(self):
        self.runs = {}

    def create_run(self, run_id, payload, status="queued"):
        self.runs[run_id] = {"id": run_id, "payload": payload, "status": status}

    def update_run_status(self, run_id, status):
        if run_id in self.runs:
            self.runs[run_id]["status"] = status

    def count_active_runs(self):
        return len([r for r in self.runs.values() if r["status"] in ("running", "cancelling")])

    def get_queued_runs(self, limit=10):
        queued = [r for r in self.runs.values() if r["status"] == "queued"]
        # return dict-like objects similar to DB layer
        return queued[:limit]

    def set_run_result(self, run_id, result):
        if run_id in self.runs:
            self.runs[run_id]["result"] = result


@pytest.mark.asyncio
async def test_dispatcher_starts_queued_runs(monkeypatch):
    # Prepare environment
    runner.EXEC_RUNS.clear()
    runner.RUN_TASKS.clear()

    fake_db = FakeDB()
    # install fake DB
    runner.storage.USE_DB = True
    runner.storage._db = fake_db

    # reduce concurrency to 1 for deterministic behavior by adjusting the
    # underlying backing attribute on the Settings instance.
    monkeypatch.setattr(runner.SETTINGS, "MAX_CONCURRENT_RUNS", 1)

    # stub run_graph to a fast noop that marks finished
    async def _stub_run_graph(initial_state, run_id=None):
        await asyncio.sleep(0.05)
        # simulate finishing
        runner.EXEC_RUNS[run_id]["status"] = "finished"
        fake_db.set_run_result(run_id, {"ok": True})
        fake_db.update_run_status(run_id, "finished")
        # call dispatcher to pick up queued runs
        runner._maybe_start_queued_runs()
        return {"ok": True}

    monkeypatch.setattr(runner, "run_graph", _stub_run_graph)

    # Start first run -> should become running immediately
    rid1 = runner.start_async_run({"input": 1}, run_id="run-1")
    # Create second run; with concurrency=1 it should be queued
    rid2 = runner.start_async_run({"input": 2}, run_id="run-2" )

    # Ensure DB recorded both runs
    assert fake_db.runs["run-1"]["status"] in ("running", "finished")
    assert fake_db.runs["run-2"]["status"] == "queued"

    # Wait for first to finish and allow dispatcher to start second
    await asyncio.sleep(0.2)

    # After dispatcher runs, the second run should have transitioned to running or finished
    assert fake_db.runs["run-2"]["status"] in ("running", "finished")

    # Cleanup tasks
    for t in list(runner.RUN_TASKS.values()):
        try:
            await t
        except Exception:
            pass
