# Segmenter Agent

Purpose

- Determine a customer's segment label based on recent events and explainable reasons.

Location

- `backend/agents/segmenter.py`

API / Contract

- Function: `segment_user(customer: dict) -> dict`
- Input: `customer` object with fields like `id`, `name`, `last_event`, `properties`.
- Output: `{ 'segment': str, 'reasons': List[str] }`

Example

```py
from agents.segmenter import segment_user

cust = { 'id': 'cust_001', 'last_event': 'started_form' }
seg = segment_user(cust)
# seg -> { 'segment': 'FormAbandoned', 'reasons': [...] }
```

Notes

- Keep logic explainable and deterministic where possible. For production, this component can call a model or ML service but should return human-readable reasons for traceability.
