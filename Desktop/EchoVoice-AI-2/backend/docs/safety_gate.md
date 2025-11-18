# Safety & Compliance Agent

Purpose
- Validate generated variants against brand, legal, and safety rules. Flag or rewrite content that violates policies.

Location
- `backend/agents/safety_gate.py`

API / Contract
- Function: `safety_check_and_filter(variants: list) -> dict`
- Input: List of variant objects.
- Output: `{ 'safe': [variants], 'blocked': [ { 'variant': variant, 'reason': str } ] }`.

Example
```py
from agents.safety_gate import safety_check_and_filter

res = safety_check_and_filter(variants)
# res['safe'] contains allowed variants, res['blocked'] contains blocked ones and reasons
```

Notes
- The scaffold uses simple prohibited-term matching. In production, implement a policy engine and safety classifier, and include a human-review path for uncertain cases.
