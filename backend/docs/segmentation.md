# 🧠 Segmentation Phase

## Phase 1 of the End-to-End AI Personalization Engine

### Overview

The Segmentation Phase is the entry point of the entire system.

Its purpose is to classify incoming user context into the most relevant analytical “segment” before any generation, compliance, or experimentation logic runs.
[cite\_start]Segmentation ensures the system behaves differently when the user expresses different underlying goals — such as intent, behavior, purchasing patterns (**RFM**), or profile-based attributes[cite: 21, 134].
This phase is implemented as a LangGraph multi-branch router, where the next node is chosen dynamically based on the user’s detected segmentation goal.

### Why Segmentation Matters

Segmentation ensures that the graph behaves purposefully, not generically:

* Different user states require different processing strategies.
* [cite\_start]Downstream agents (compliance, generation, experiments) rely on “segment awareness”[cite: 137, 138].
* It reduces model confusion and improves determinism.
* [cite\_start]It enables A/B experimentation to differentiate segment-specific patterns[cite: 154].
* [cite\_start]It creates **explainable reasons** for personalization, which is a core system feature[cite: 23, 77, 164].

### Flow Breakdown

1. **Start Segmentation Phase**
    This is the entry trigger into the segmentation pipeline. The system receives structured input.

2. **Goal Router**
    A lightweight, deterministic routing node. It evaluates the message and context to determine which segmentation strategy to apply.

| Signal Type | Example | Routed To |
| :--- | :--- | :--- |
| **RFM** | Purchase history, frequency of actions | RFM Segmentation |
| **Intent** | User goals, questions, objectives | Intent Segmentation |
| **Behavioral** | Patterns in interaction, sentiment, pacing | Behavioral Segmentation |
| **Profile** | Age group, skill level, domain, expertise | Profile Segmentation |

### Segmentation Engines

Each segmentation module is an independent LangGraph node with its own logic and output structure. They **MUST** produce standardized payloads for the subsequent phases (Phase 2, 3, 4) to consume them seamlessly.

* **RFM Segmentation:** Focuses on Recency, Frequency, and Monetary value for personalization flows like priority queueing or retention strategies.
* **Intent Segmentation:** Extracts user intention (Ask a question, Request analysis, etc.). This is often the most heavily weighted segment because it drives downstream agent behavior.
* **Behavioral Segmentation:** Analyzes user behavior patterns like tone or emotional markers to adjust compliance thresholds or experiment selection.
* **Profile Segmentation:** Based on attributes such as domain expertise or technical level. Used to tune generation formatting, verbosity, or compliance strictness.

### Priority Assignment & Output

After each module completes segmentation, the system merges results into a priority computation node:

* **Why prioritize?** Because more than one segmentation can be relevant at once.
* **How it works:** Each module contributes a score and justification. The system ranks them, and the highest-priority segment becomes the **Final Prioritized Segment**.

### Final Prioritized Segment (Revised State Definition)

This is the output of the entire Segmentation Phase. [cite\_start]It becomes the authoritative **context label** and **justification** for downstream flows[cite: 164].

**Example Final Output (State Update):**

```json
{
  "final_segment": "intent:clarification",
  "confidence": 0.88,
  "segment_description": "User is a 'high-value shopper' seeking 'clarification on product nutritional facts' to match their 'health-conscious' profile.",
  "raw_segments": {
    "intent": {...},
    "behavior": {...},
    // ... all raw segment data
  }
}
```

## **Implementation Notes (LangGraph Python)**

* `GoalRouter` is implemented via a branching LangGraph node.
* Each segmentation module is a separate graph node.
* All paths converge into the `priority_and_output` node.
* The prioritized output, including the critical `segment_description`, is written into the graph state.
* Downstream phases read this without re-computing segmentation.

-----
