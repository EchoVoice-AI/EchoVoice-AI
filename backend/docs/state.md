
# GraphState (Canonical State)

**Canonical:** The pipeline uses a single shared `GraphState` as the canonical state object passed between nodes.

**Purpose:** Nodes read and write keys on `GraphState` (e.g., `campaign_goal`, `user_message`, `final_segment`, `confidence`).

**Why:** Using one TypedDict avoids type drift and confusion between phase-local dataclasses and the runtime's state wrapper.

**Guidance for contributors:**

- Prefer updating `GraphState` for cross-phase signals.
- If you need phase-local temporary data, namespace it under a key (for example `state['segmentation'] = {...}`) rather than creating a separate `*State` dataclass unless you also wire a true subgraph with its own StateGraph.
- When running in LangGraph Studio, the runtime may wrap the active values under `{'values': {...}}` — nodes in this codebase normalize for that shape.

This note documents the project decision to maintain a single shared state to reduce accidental data loss and simplify debugging.
