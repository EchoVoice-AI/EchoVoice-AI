# **Step 1 — Overview / Introduction**

## Original excerpt

> The Segmentation Phase is the entry point of the entire system.
> Its purpose is to classify incoming user context into the most relevant analytical “segment” before any generation, compliance, or experimentation logic runs.

### Revised version (LangGraph-style)

```markdown
# 🧠 Segmentation Phase

## Phase 1: Entry Point of the AI Personalization Engine

The Segmentation Phase is the **initial step** in the end-to-end personalization workflow. Its goal is to classify each user interaction into the **most relevant segment** before any generation, compliance, or experimentation logic occurs.  

Segmentation ensures that the system can:

- Handle different user states with **purposeful, tailored processing**.
- Provide **explainable reasoning** for decisions, enabling transparency and auditability.
- Improve **determinism** and reduce model confusion.
- Support **A/B experimentation** with segment-specific variations.
- Inform downstream phases (message generation, compliance checks, experiments) with **segment-aware context**.

> This phase is implemented as a **LangGraph multi-branch router**, where the next node is dynamically selected based on the detected segmentation goal.
```

---

## Inputs & Produced Outputs (contract)

**Inputs (expected in `GraphState`):**

- `campaign_goal` (str) — high-level campaign intent such as `retention_offer`, `increase_engagement`, or `reduce_churn`.
- `user_message` (str | None) — conversational input or user text; optional for silent/background segmentation.
- `raw_user_data` (optional) — service-specific raw signals (purchase history, activity metrics, profile attributes).

**Produced / Modified Fields:**

- `_selected_segment` (optional) — router hint identifying the segmentation engine chosen (e.g., `RFM_SEGMENTATION`).
- `raw_segments` (dict) — raw outputs from each segmentation engine keyed by engine name (isolated, explainable payloads).
- `_segments_for_priority` (list) — list of normalized {segment, score, details} items used by the priority node.
- `final_segment`, `confidence`, `segment_description` — written by the priority node after merging and boosting.

Refer to `docs/state.md` and `src/agent/state.py` for the canonical `GraphState` TypedDict describing the full pipeline contract.

## Runtime Shape & Wrapper Note

Some LangGraph runtimes (including Studio and hosted runners) wrap the live state under a `values` key. Implementations should:

- Accept either the direct state shape or a runtime-wrapped shape (i.e., read `state.get("values", state)` before accessing fields).
- Return deltas/patches that update state rather than replacing the entire state object. Returning a small dict like `{"raw_segments": {...}}` avoids accidental loss of other fields (for example, `campaign_goal`).

## Node Responsibilities (brief)

- **Goal Router:** Deterministically selects the segmentation engine (writes `_selected_segment` as a hint, optional).
- **Segmentation Engines:** Independently produce `raw_segmentation_data` payloads with `label`, `confidence`, and `justification`.
- **Priority Node:** Merges module outputs, applies router boosts, and writes `final_segment`, `confidence`, and a human-friendly `segment_description`.

## Observability & Auditing

Each segmentation engine should include an explicit `justification` string and preserve raw inputs used to compute that justification. Store those raw signals under `raw_segments` so audits can replay decisions. Consider writing to a lightweight `segmentation_log` or `compliance_log` for downstream traceability.

## Error Handling & Fallbacks

- If required inputs are missing (e.g., `campaign_goal` and `user_message` both empty), the router should fall back to `PROFILE` segmentation.
- If all engines return low confidence (configurable threshold), the priority node should emit a low-confidence flag and select the fallback segment.

## Security / PII Guidance

Do not persist raw PII in long-term storage. If any `raw_user_data` contains sensitive fields, redact or hash them before writing to persistent logs. Keep ephemeral, unredacted data only in memory/state for immediate processing.

## Quick Example UX Flow

1. Router picks `RFM_SEGMENTATION` based on `campaign_goal`.
2. `rfm_segmenter` writes `raw_segments["rfm"]` with `label`, `confidence`, `justification`.
3. Priority node ranks segments and writes `final_segment`.
4. Generation nodes read `final_segment` and condition prompts accordingly.

## Extending the Phase

To add a new segmentation engine:

- Implement a LangGraph node that produces `raw_segmentation_data` with the required fields.
- Add the engine key to the router's decision logic and update any priority-boost rules.
- Add unit tests validating the new engine's output shape and priority interactions.

---

### ✅ Key Changes Made

1. Added **phase numbering and context** to match LangGraph style.
2. Turned benefits into a bullet list — easier to scan.
3. Introduced the **LangGraph multi-branch router concept** early.
4. Emphasized **segment awareness for downstream phases**.

---

## **Step 2 — Flow Breakdown & Goal Router**

### Overview

The **Goal Router** is a lightweight, deterministic node in the Segmentation Phase. It decides **which segmentation engine** should handle a given user message based on:

- `campaign_goal` signals (e.g., retention, churn, engagement)
- `user_message` content (questions, requests, or instructions)

The router ensures that each input is handled by the most relevant segmentation logic, and the output of this router becomes the **initial routing context** for downstream nodes.

---

### **Routing Signals Table**

| Signal Type    | Example Input                                                   | Routed To               | Description                                                                                       |
| -------------- | --------------------------------------------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------- |
| **RFM**        | `"retention_offer"`, `"reduce churn"`                           | RFM Segmentation        | Uses Recency, Frequency, Monetary (RFM) patterns for loyalty, retention, and purchasing behavior. |
| **Intent**     | `"How do I return a product?"`, `"Tell me about your pricing"`  | Intent Segmentation     | Extracts user goals, questions, or objectives for personalized response handling.                 |
| **Behavioral** | `"I want to increase engagement"`, `"real-time activity check"` | Behavioral Segmentation | Detects behavioral patterns, sentiment, or pacing to adjust downstream compliance or experiments. |
| **Profile**    | N/A / fallback                                                  | Profile Segmentation    | Default route based on profile attributes (age, skill, expertise) when no other signal applies.   |

---

### **Routing Logic (Priority Order)**

The router uses **strict priority rules**:

1. **RFM Segmentation**

   - Matches if `campaign_goal` contains: `"churn"`, `"retention"`, or `"loyalty"`.
   - **Highest priority**: campaign goal dominates over user message.

2. **Intent Segmentation**

   - Matches if `user_message` contains: `"ask"`, `"?"`, `"tell me about"`.
   - Used when **user queries** are detected and RFM doesn’t match.

3. **Behavioral Segmentation**

   - Matches if `campaign_goal` mentions: `"engagement"`, `"real-time"`, `"activity"`.

4. **Profile Segmentation (Fallback)**

   - Default route when none of the above conditions match.

> The router’s decision is returned as a **node key**, which LangGraph uses to branch into the correct segmentation engine.

---

### **Example**

```python
state = {
    "campaign_goal": "retention_offer",
    "user_message": "What's the price for the premium plan?"
}

selected_node = goal_router(state)
print(selected_node)
# Output: "RFM_SEGMENTATION" 
# RFM dominates because the campaign goal indicates retention, even though user asks a question
```

---

### ✅ Key Notes

- The router is **deterministic**: same input → same node.
- It produces `_selected_segment` in the graph state for later priority computation.
- Even if multiple signals apply (e.g., campaign + question), **priority rules** determine the final route.
- This enables downstream nodes (priority assignment, message generation) to consume segmentation-aware context **without re-computing routing logic**.

---

## **Step 3 — Segmentation Engines**

Each segmentation module is implemented as an independent **LangGraph node**. These modules **must produce standardized outputs** for downstream phases (priority, generation, compliance, experimentation) to consume seamlessly.

---

## **1. RFM Segmentation**

**Purpose:**
Focuses on **Recency, Frequency, and Monetary** behavior for personalization flows like retention, loyalty, or priority queueing.

**Typical Signals:**

- `campaign_goal` includes `"churn"`, `"retention"`, `"loyalty"`
- Purchase history, number of interactions, average order value

**Input State Example:**

```json
{
  "campaign_goal": "reduce_churn",
  "user_message": "",
  "raw_user_data": {
    "last_purchase_days": 10,
    "total_orders": 15,
    "average_order_value": 120
  }
}
```

**Output Payload (Standardized):**

```json
{
  "raw_segmentation_data": {
    "rfm": {
      "label": "high_value",
      "confidence": 0.92,
      "justification": "User purchased frequently and recently with high average order value"
    }
  }
}
```

---

## **2. Intent Segmentation**

**Purpose:**
Detects **user intent** from conversational input. Often the most influential segment since it drives downstream agent behavior.

**Typical Signals:**

- `user_message` contains questions or commands
- Keywords like `"?"`, `"ask"`, `"tell me about"`

**Input State Example:**

```json
{
  "campaign_goal": "increase_awareness",
  "user_message": "How do I return a product?"
}
```

**Output Payload (Standardized):**

```json
{
  "raw_segmentation_data": {
    "intent": {
      "label": "question:return_policy",
      "confidence": 0.87,
      "justification": "User explicitly asks about the return process"
    }
  }
}
```

---

## **3. Behavioral Segmentation**

**Purpose:**
Analyzes user **interaction patterns, emotional tone, and pacing** to adapt compliance thresholds or experimental targeting.

**Typical Signals:**

- Campaign goals: `"engagement"`, `"real-time"`, `"activity"`
- Frustration or sentiment in `user_message`

**Input State Example:**

```json
{
  "campaign_goal": "improve_engagement",
  "user_message": "I'm really frustrated that checkout is slow"
}
```

**Output Payload (Standardized):**

```json
{
  "raw_segmentation_data": {
    "behavioral": {
      "label": "frustrated_user",
      "confidence": 0.91,
      "justification": "User expresses clear frustration with the checkout experience"
    }
  }
}
```

---

## **4. Profile Segmentation**

**Purpose:**
Categorizes users based on **profile attributes** like expertise, age group, or domain. Often serves as a fallback when other signals are weak.

**Typical Signals:**

- Age group, skill level, industry, domain expertise
- Empty or generic `user_message`

**Input State Example:**

```json
{
  "campaign_goal": "general_outreach",
  "user_message": ""
}
```

**Output Payload (Standardized):**

```json
{
  "raw_segmentation_data": {
    "profile": {
      "label": "default_profile",
      "confidence": 0.50,
      "justification": "No specific signals; default profile assigned"
    }
  }
}
```

---

 ✅ Key Notes

- Each module **produces a `raw_segmentation_data` object** with:

  - `label` → human-readable segment name
  - `confidence` → score between 0.0 and 1.0
  - `justification` → explainable reasoning for auditability

- All modules are **isolated LangGraph nodes**, allowing independent testing and subgraph execution.

- Downstream nodes **merge these outputs** for final priority assignment.

---

Perfect! Let’s go through **Steps 4–7** in a single coherent doc, following the LangGraph style. I’ll cover **priority assignment, final output, integration with downstream nodes, and implementation notes**.

---

## **Step 4 — Priority Assignment & Output**

After all segmentation modules complete, the system must **determine which segment takes precedence**. Multiple signals may match simultaneously, so we compute **scores and justification** to select the **Final Prioritized Segment**.

### **Priority Computation**

- Each module contributes:

  - `segment` (e.g., `rfm:high_value`, `intent:question:return_policy`)
  - `score` (float 0.0–1.0)
  - `details` / `justification`

- The system **boosts the router-selected module** to ensure deterministic routing wins when multiple segments are valid.

- Scores are **ranked**, and the **highest-priority segment** becomes the **authoritative segment** for downstream nodes.

---

### **Example Input to Priority Node**

```json
{
  "_segments_for_priority": [
    {"segment": "rfm:high_value", "score": 0.92, "details": {"justification": "Recent, frequent, high-value purchases"}},
    {"segment": "intent:question:return_policy", "score": 0.87, "details": {"justification": "User asks about returns"}},
    {"segment": "behavioral:frustrated_user", "score": 0.91, "details": {"justification": "Frustration expressed"}},
    {"segment": "profile:default_profile", "score": 0.50, "details": {}}
  ]
}
```

---

### **Output of Priority Node**

```json
{
  "final_segment": "rfm:high_value",
  "confidence": 0.95,
  "segment_description": "High-value shopper with recent frequent purchases. Retention/loyalty priority triggered.",
  "raw_segments": {
    "rfm": {...},
    "intent": {...},
    "behavioral": {...},
    "profile": {...}
  }
}
```

> The `final_segment` is **authoritative**: downstream nodes read it without recomputing segmentation.

---

## **Step 5 — Downstream Integration (Generation, Experiments, Deployment)**

Once the final segment is selected, it feeds all subsequent phases:

1. **Message Generation**

   - Uses `final_segment` to condition prompts for personalized responses.
   - Example: `"Respond for segment: rfm:high_value. Input: 'What's the premium plan price?'"`

2. **Experimentation & Variant Selection**

   - A/B/n experiments can use `final_segment` to assign **segment-aware variants**.
   - Example: Users in `intent:question:return_policy` may receive one set of message variants, while `rfm:high_value` users receive another.

3. **Deployment**

   - Selected message variants are deployed, and metadata is tracked.
   - Segmentation ensures **consistent behavior across campaigns**.

---

## **Step 6 — Raw State Storage Best Practices**

LangGraph recommends storing **raw, unformatted data** in the state:

- Keep **raw signals** from each segmentation module.
- Do **not store prompt templates or formatted outputs** in the state.
- Compute formatted content **on-demand** in generation nodes.

**Benefits:**

- Easier debugging and auditability
- Allows multiple downstream nodes to use same raw data differently
- Makes subgraphs and reruns deterministic

---

### **Raw State Example**

```json
{
  "campaign_goal": "retention_offer",
  "user_message": "What's the price for the premium plan?",
  "final_segment": "rfm:high_value",
  "confidence": 0.95,
  "segment_description": "High-value shopper with recent frequent purchases. Retention/loyalty priority triggered.",
  "raw_segments": {
    "rfm": {"label": "high_value", "confidence": 0.92, "justification": "..."},
    "intent": {"label": "question:return_policy", "confidence": 0.87, "justification": "..."},
    "behavioral": {"label": "frustrated_user", "confidence": 0.91, "justification": "..."},
    "profile": {"label": "default_profile", "confidence": 0.50, "justification": "..."}
  }
}
```

---

## **Step 7 — Implementation Notes (LangGraph Python)**

- **GoalRouter Node:** decides which segmentation node to call; writes `_selected_segment` in state.
- **Segmentation Nodes:** produce standardized `raw_segmentation_data` payloads.
- **Priority Node:** merges module outputs, applies boosts, and writes `final_segment`, `confidence`, and `segment_description`.
- **Downstream Nodes:**

  - `generation_node` formats prompts using `final_segment`
  - `experimentation_node` uses segment to select variants
  - `deployment_node` records deployment status

**Key principles:**

1. **State is shared memory:** All nodes read/write to the same dictionary.
2. **Keep state raw:** Only store unformatted signals and segment results.
3. **Nodes handle routing internally:** Graph edges are minimal; branching is deterministic via GoalRouter.
4. **Explainable output:** `segment_description` ensures reasoning is transparent and auditable.
5. **Error handling:** transient errors retry, LLM errors store context, human-fixable errors pause via `interrupt()`.

---

### ✅ Summary of Segmentation Phase

- Segmentation is **phase 1** of the pipeline.
- **GoalRouter** dynamically selects RFM, Intent, Behavioral, or Profile segmentation.
- **Raw outputs** from modules feed **priority node** → `final_segment`.
- **Final segment** informs downstream message generation, experimentation, and deployment.
- **State stores raw signals** for auditability, reproducibility, and subgraph flexibility.

---
