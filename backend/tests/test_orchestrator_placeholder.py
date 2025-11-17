import pytest

from app.graph.orchestrator import Orchestrator
from app.store import store


@pytest.mark.asyncio
async def test_orchestrator_placeholder_run_flow():
    orch = Orchestrator(store_=store)
    payload = {"id": "placeholder-1", "email": "ph@example.com"}
    result = await orch.run_flow("placeholder_flow", payload)

    assert isinstance(result, dict)
    # New orchestrator run returns detailed flow output (segment/citations/analysis)
    assert "segment" in result
    assert "analysis" in result

    # cleanup keys stored by the orchestrator
    store.delete("placeholder-1:segment")
    store.delete("placeholder-1:citations")
    store.delete("placeholder-1:variants")
    store.delete("placeholder-1:analysis")
    store.delete("placeholder-1:winner")
