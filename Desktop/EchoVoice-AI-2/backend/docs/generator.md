# Generator Agent

Purpose

- Generate personalized message variants (A/B/n) using segment data and retrieved citations.

Location

- `backend/agents/generator.py`

API / Contract

- Function: `generate_variants(customer: dict, segment: dict, citations: list) -> list`
- Input: `customer`, `segment` (from segmenter), and `citations` (from retriever).
- Output: List of variant objects: `{ 'id': str, 'subject': str, 'body': str, 'meta': dict }`.

Example

```py
from agents.generator import generate_variants

variants = generate_variants(customer, segment, citations)
# variants -> [ { 'id': 'A', 'subject': '...', 'body': '...' }, { 'id': 'B', ... } ]
```

Notes

- Keep citations attached or embedded so downstream safety checks can reference sources.
- For production, generator can call an LLM with a prompt template and strict answer format to ensure structured output.
