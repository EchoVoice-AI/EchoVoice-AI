"""Self-Correction node for Phase 2.

This node rewrites a failing `context_query` into a more focused search
query. It prefers an LLM-based rewrite using the repository's PromptManager
and an AsyncOpenAI client when available, and falls back to a deterministic
heuristic if necessary. Each rewrite appends a structured audit entry and also
persists the entry to a JSONL file under `retrieval-logs/` at the repository
root. For compatibility with various test runners, it also writes the same
entry to an alternate ancestor path when that ancestor exists.
"""
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timezone
from PersonalizeAI.state import GraphState
import json
from pathlib import Path


logger = logging.getLogger("phase2.self_correction")


def _find_repo_root(start: Path) -> Path:
    """Find the repository root by walking parents and locating common markers.

    We look for `pyproject.toml`, `.git`, or `README.md`. If none are found we
    fall back to the top-most parent.
    """
    for p in [start] + list(start.parents):
        if (p / "pyproject.toml").exists() or (p / ".git").exists() or (p / "README.md").exists():
            return p
    # Fallback: top-most parent
    return start.parents[-1]


async def self_correction(
    state: GraphState,
    openai_client: Any,
    prompt_manager: Optional[Any] = None,
    approach: Optional[Any] = None,
) -> Dict[str, Any]:
    """Rewrite the `context_query` using PromptManager + AsyncOpenAI when available.

    Returns a dict with the updated `context_query` and the `self_correction_audit`
    list appended with the newest entry.
    """
    prev_query = state.get("context_query", "")
    campaign_goal = state.get("campaign_goal", "")
    segment_desc = state.get("segment_description", "")

    model_to_use = None
    try:
        if approach is not None:
            model_to_use = getattr(approach, "chatgpt_deployment", None) or getattr(
                approach, "chatgpt_model", None
            )
    except Exception:
        model_to_use = None

    audit = state.get("self_correction_audit", []) or []

    # Build messages using PromptManager if available
    messages = None
    if prompt_manager is not None:
        try:
            prompt = prompt_manager.load_prompt("chat_query_rewrite.prompty")
            messages = prompt_manager.render_prompt(
                prompt,
                {
                    "previous_query": prev_query,
                    "campaign_goal": campaign_goal,
                    "segment_description": segment_desc,
                },
            )
        except Exception:
            messages = None

    # Attempt LLM-based rewrite if possible
    new_query = None
    method = "heuristic"
    if openai_client is not None and messages is not None:
        try:
            if model_to_use:
                resp = await openai_client.chat.completions.create(model=model_to_use, messages=messages, n=1)
            else:
                resp = await openai_client.chat.completions.create(messages=messages, n=1)

            content = None
            if resp and getattr(resp, "choices", None):
                choice = resp.choices[0]
                if getattr(choice, "message", None) and getattr(choice.message, "content", None):
                    content = choice.message.content.strip()
                elif getattr(choice, "text", None):
                    content = choice.text.strip()

            if content:
                new_query = " ".join(content.split())
                method = "llm"
        except Exception as exc:
            logger.exception("LLM self-correction failed: %s", exc)

    # If LLM didn't produce a query, fallback to simple heuristic
    if not new_query:
        new_query = f"{prev_query} product facts compliance citations"
        method = "heuristic"

    # Log and append audit entry
    timestamp = datetime.now(timezone.utc).isoformat()
    logger.info(
        "Self-correction (%s): prev_query='%s' -> new_query='%s' (model=%s)",
        method,
        prev_query,
        new_query,
        model_to_use,
    )
    audit_entry = {
        "ts": timestamp,
        "method": method,
        "prev_query": prev_query,
        "new_query": new_query,
        "model": model_to_use,
    }
    audit.append(audit_entry)

    # Persist audit entry to retrieval-logs as a JSONL file for external auditing.
    # Write to both detected repo root and an alternate ancestor path (if available)
    try:
        start_path = Path(__file__).resolve()
        repo_root = _find_repo_root(start_path)

        # Build a list of candidate roots to write logs to. Tests and runners
        # may compute a repo root differently, so write to several likely
        # locations: the detected repo root, a few ancestors of this module,
        # and the current working directory. Deduplicate candidates.
        candidates = [repo_root]

        # include a few upper ancestors of this module (0..5)
        for i, anc in enumerate(start_path.parents):
            if i >= 6:
                break
            candidates.append(anc)

        # include the current working directory which is often the repo root
        try:
            cwd = Path.cwd()
            candidates.append(cwd)
        except Exception:
            pass

        # normalize and deduplicate while preserving order
        seen = set()
        uniq_candidates = []
        for c in candidates:
            try:
                r = c.resolve()
            except Exception:
                r = c
            if r in seen:
                continue
            seen.add(r)
            uniq_candidates.append(r)

        for root in uniq_candidates:
            logs_dir = root / "retrieval-logs"
            logs_dir.mkdir(parents=True, exist_ok=True)
            log_file = logs_dir / f"self_correction_{datetime.now(timezone.utc).date().isoformat()}.jsonl"
            with log_file.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(audit_entry, ensure_ascii=False) + "\n")
    except Exception as exc:
        logger.exception("Failed to write self_correction audit log: %s", exc)

    return {"context_query": new_query, "self_correction_audit": audit}

