# Segmenter Agent

# segmenter.py — Documentation

This document describes the purpose, usage, and behavior of backend/agents/segmenter.py.

## Overview

segmenter.py provides a small utility for turning simple customer event records into marketing/sales segments. It contains:

- simple helpers to coerce values (`to_bool`) and prettify slugs (`prettify_slug`),
- a `segment_user` function that classifies a single customer record into a funnel stage with an intent level and human-readable reasons, and
- a `load_customers_from_csv` helper to read customer rows from a CSV file.

It also includes a small CLI-style manual test that can be run as a module.

## Quick start / Running the simple manual test

From the repository root (or `backend`), run:

    cd backend
    python -m agents.segmenter

This will attempt to load `data/customer_events.csv` from the project root and print segmentation results for each row.

## Expected CSV format

`load_customers_from_csv` reads CSV files using `csv.DictReader` and returns a list of dictionaries. The segmentation logic expects (but does not strictly require) the following columns:

- `user_id` — optional identifier (string)
- `email` — optional email (string)
- `viewed_page` — page or flow the user viewed (string, e.g. "payment_plans")
- `form_started` — whether they started a form/flow (strings such as "yes"/"no", case-insensitive)
- `scheduled` — whether they scheduled a next step (e.g. a call/session) (strings such as "yes"/"no")
- `attended` — whether they attended/completed the scheduled step (strings such as "yes"/"no")

Any additional columns are preserved in the row dictionaries but ignored by segmentation logic.

CSV is opened with UTF-8 encoding and newline handling enabled (newline="").

## API

### to_bool(value) -> bool

Coerces a value to boolean using permissive string matching.

- Treats `None` as `False`.
- Converts the value to string, strips whitespace, lowercases it, and returns `True` when the result is one of:
  - "yes", "y", "true", "1"
- Any other value returns `False`.

Notes:
- This is intentionally permissive for user-entered CSV values.
- Values like `"True"`, `"YES"`, `"1"`, and `"y"` will be recognized as true.

### prettify_slug(value) -> str

Turns a slug-like string into a human-friendly label.

- If `value` is falsy (None, empty string, etc.), returns `"Unknown"`.
- Otherwise replaces `-` and `_` with spaces and `.title()`-cases the result.

Examples:
- `"payment_plans"` -> `"Payment Plans"`
- `""` -> `"Unknown"`

### segment_user(customer: dict) -> dict

Main segmentation function. Accepts a dictionary representing a customer's events (usually from CSV). It uses the keys `viewed_page`, `form_started`, `scheduled`, and `attended` to determine the user segment.

Input:
- `customer` — dict-like mapping. Keys are read using `customer.get(...)`. Values are typically strings from CSV.

Behavior:
1. Read and normalize:
   - `viewed_page` is normalized to a lowercased string; if absent, `use_case` becomes `"unknown"`.
   - `form_started`, `scheduled`, `attended` are coerced to booleans using `to_bool`.

2. Determine funnel stage (priority order):
   - If `attended` is true:
     - funnel_stage: `"CompletedScheduledStep"`
     - intent_level: `"very_high"`
     - reasons: `["completed a scheduled step (call/session/meeting)", "shows very strong commitment"]`
   - Else if `scheduled` is true:
     - funnel_stage: `"ScheduledNextStep"`
     - intent_level: `"high"`
     - reasons: `["scheduled a next step but has not completed it yet", "shows strong intent"]`
   - Else if `form_started` is true:
     - funnel_stage: `"StartedFormOrFlow"`
     - intent_level: `"medium"`
     - reasons: `["started a form or flow but did not finish", "shows interest and may need a nudge"]`
   - Else:
     - funnel_stage: `"BrowsingOnly"`
     - intent_level: `"low"`
     - reasons: `["viewed a page but did not start the flow", "early-stage interest"]`

3. Compose outputs:
   - `use_case` — normalized slug (lowercased string or `"unknown"`)
   - `use_case_label` — human-friendly label from `prettify_slug`
   - `segment` — f"{use_case}:{funnel_stage}"
   - `reasons` — list with the first entry set to `"interested in: {use_case_label}"` and the rest the stage-specific reasons

Return structure:
```
{
  "segment": <str>,          # "<use_case>:<funnel_stage>"
  "use_case": <str>,         # normalized use case slug or "unknown"
  "use_case_label": <str>,   # pretty label like "Payment Plans" or "Unknown"
  "funnel_stage": <str>,     # one of CompletedScheduledStep, ScheduledNextStep, StartedFormOrFlow, BrowsingOnly
  "intent_level": <str>,     # one of very_high, high, medium, low
  "reasons": <list[str]>     # list of reasons (first entry always "interested in: <label>")
}
```

Example:
Input:
```
{
  "user_id": "U001",
  "email": "a@example.com",
  "viewed_page": "payment_plans",
  "form_started": "yes",
  "scheduled": "no",
  "attended": "no"
}
```

Output:
```
{
  "segment": "payment_plans:StartedFormOrFlow",
  "use_case": "payment_plans",
  "use_case_label": "Payment Plans",
  "funnel_stage": "StartedFormOrFlow",
  "intent_level": "medium",
  "reasons": [
    "interested in: Payment Plans",
    "started a form or flow but did not finish",
    "shows interest and may need a nudge"
  ]
}
```

### load_customers_from_csv(csv_path: str) -> list[dict]

Reads `csv_path` using `csv.DictReader` and returns a list of rows (each a dict where keys are column headers). Typical use is to call this and then pass each row to `segment_user`.

Behavior notes:
- Values are returned as strings (or empty strings) — use `to_bool` inside segmentation to interpret boolean-like columns.
- Uses UTF-8 encoding and newline="" for portability.

## Edge cases and behavior notes

- If `viewed_page` is missing or empty, the `use_case` becomes `"unknown"` and `use_case_label` becomes `"Unknown"`.
- `to_bool` is the single source of truth for interpreting truthy values from CSV; any non-matching strings are treated as `False`.
- `segment_user` does not raise on missing keys; it uses `.get(...)` and default fallbacks.
- `segment_user` explicitly prioritizes `attended` over `scheduled` over `form_started`. If multiple are true, the highest priority branch wins.

## Suggested improvements

- Add type annotations and a dataclass (e.g., `CustomerEvent`) for clearer input expectations.
- Add unit tests for `to_bool`, `prettify_slug`, and `segment_user`, including boundary cases.
- Make funnel stage labels and reasons configurable from a settings file so they can be localized or changed without code edits.
- Consider returning an enum or constants for `funnel_stage` and `intent_level` to avoid magic strings across the codebase.

## Files & locations

- Implementation: `backend/agents/segmenter.py`
- Sample CSV (expected by the manual test): `data/customer_events.csv` (project root)

## License and authorship

See project repository for license and authorship information.
