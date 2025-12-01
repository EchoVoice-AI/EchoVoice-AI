import asyncio
import json
from types import SimpleNamespace
from pathlib import Path

import pytest

from PersonalizeAI.nodes.phase2_retrieval import self_correction


class FakePromptManager:
    def load_prompt(self, path: str):
        return "fake-prompt"

    def render_prompt(self, prompt, data):
        # Return a chat messages list compatible with the AsyncOpenAI chat API
        return [{"role": "user", "content": f"Rewrite: {data.get('previous_query')}"}]


class FakeOpenAI:
    def __init__(self, content: str):
        self.chat = SimpleNamespace()
        async def create(*args, **kwargs):
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])

        self.chat.completions = SimpleNamespace(create=create)


@pytest.mark.asyncio
async def test_self_correction_with_llm(tmp_path):
    state = {"context_query": "old query", "campaign_goal": "Reduce churn", "segment_description": "high value"}
    fake_openai = FakeOpenAI("concise rewritten query")
    pm = FakePromptManager()
    # call self_correction
    update = await self_correction.self_correction(state, fake_openai, prompt_manager=pm, approach=None)
    assert "context_query" in update
    assert update["context_query"] == "concise rewritten query"
    assert "self_correction_audit" in update
    audit = update["self_correction_audit"]
    assert isinstance(audit, list) and len(audit) >= 1
    assert audit[-1]["method"] in ("llm", "heuristic")

    # Check that a log file was created in repo retrieval-logs
    repo_root = Path(__file__).resolve().parents[2]
    log_dir = repo_root / "retrieval-logs"
    files = list(log_dir.glob("self_correction_*.jsonl"))
    assert files, "Expected at least one self_correction log file"
    # read last line of last file and validate JSON structure
    with files[-1].open("r", encoding="utf-8") as fh:
        lines = fh.readlines()
    assert lines, "Log file should have entries"
    last = json.loads(lines[-1])
    assert last.get("new_query") == update["context_query"]


@pytest.mark.asyncio
async def test_self_correction_heuristic_fallback():
    state = {"context_query": "old query", "campaign_goal": "", "segment_description": ""}
    # No openai client provided -> heuristic
    update = await self_correction.self_correction(state, None, prompt_manager=None, approach=None)
    assert "context_query" in update
    assert "product facts" in update["context_query"]
    assert "self_correction_audit" in update
    assert update["self_correction_audit"][-1]["method"] == "heuristic"
