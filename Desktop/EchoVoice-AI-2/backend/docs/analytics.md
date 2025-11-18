# Analytics / Experiment Analyst Agent

Purpose

- Simulate or compute performance metrics (CTR estimates, conversion lift) for variants and select a winning variant for delivery or further testing.

Location

- `backend/agents/analytics.py`

API / Contract

- Function: `evaluate_variants(variants: list, customer: dict) -> dict`
- Input: `variants` list and optional `customer` object.
- Output: `{ 'results': [ { 'variant_id': str, 'ctr': float } ], 'winner': { 'variant_id': str, 'ctr': float } }`

Example

```py
from agents.analytics import evaluate_variants

analysis = evaluate_variants(variants, customer)
# analysis['winner'] gives the chosen variant by simulated metric
```

Notes

- The scaffold uses randomized CTRs. Replace with real analytics integration (A/B test tracking, historical models, or a bandit algorithm) in production.
