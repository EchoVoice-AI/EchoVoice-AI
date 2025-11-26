# Backend - Debug Endpoints

This document describes the debug endpoints for development and testing of the personalization pipeline.

**Dev-only:** These routers are mounted only when the `ECHO_DEBUG` environment variable is set to `1`, `true`, or `yes`.

---

## 1. GET /debug/deliveries - Email Previews for UI

**Purpose:** Run the orchestrator for a small set of mock customers and return minimal email preview objects (subject and body) for UI preview.

### Query parameters

- `mock` (optional, boolean): When `true`, returns precomputed previews without running the pipeline.

## Response shape

The endpoint returns JSON with the top-level key `previews`, an array of preview objects.
Each preview contains:

- `user_id` (string)
- `email` (string)
- `subject` (string | null)
- `body` (string | null)
- `variant_id` (string | null)
- `blocked` (boolean) — true when no safe variant is available
- `error` (string | null) — set when pipeline execution fails for that user

Example (mock response):

```json
{
  "previews": [
    {
      "user_id": "U001",
      "email": "emma@example.com",
      "subject": "Hi Emma, quick note about running shoes",
      "body": "Hi Emma,\n\nWe thought you might like this: …\n\n— Team",
      "variant_id": "A",
      "blocked": false,
      "error": null
    },
    {
      "user_id": "U002",
      "email": "liam@example.com",
      "subject": "Liam, more on the Acme plan",
      "body": "Hello Liam,\n\nDetails: …\nLearn more on our site.",
      "variant_id": "B",
      "blocked": false,
      "error": null
    }
  ]
}
```

Example (live response with a pipeline error for a user):

```json
{
  "previews": [
    {
      "user_id": "U001",
      "email": "emma@example.com",
      "subject": "S A",
      "body": "B A",
      "variant_id": "A",
      "blocked": false,
      "error": null
    },
    {
      "user_id": "U002",
      "email": "liam@example.com",
      "subject": null,
      "body": null,
      "variant_id": null,
      "blocked": false,
      "error": "pipeline failed"
    }
  ]
}
```

## How to use locally

1. Enable the debug router and start the server (PowerShell):

```powershell
$env:ECHO_DEBUG = '1'
E:/EchoAI/EchoVoice-AI/venv/Scripts/python.exe -m uvicorn backend.app.main:app --reload
```

2. Test GET /debug/deliveries (mock):

```powershell
curl "http://127.0.0.1:8000/debug/deliveries?mock=true"
```

3. Test GET /debug/deliveries (run pipeline):

```powershell
curl "http://127.0.0.1:8000/debug/deliveries"
```

4. Test POST /debug/run (full pipeline debug):

```powershell
$body = @{customer = @{id = "U001"; name = "Emma"; email = "emma@example.com"}} | ConvertTo-Json
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/debug/run" -ContentType "application/json" -Body $body
```

---

## 2. POST /debug/run - Full Pipeline Debug

**Purpose:** Run the full orchestrator pipeline for a single customer and return the complete MessageState (all intermediate results) for debugging.

### Request body

```json
{
  "customer": {
    "id": "U001",
    "name": "Emma",
    "email": "emma@example.com",
    "last_event": "viewed_product",
    "properties": {
      "segment": "high_value"
    }
  }
}
```

### Response

Returns the full orchestrator result including all pipeline stages:

```json
{
  "segment": {"category": "high_value", "confidence": 0.95},
  "citations": ["Knowledge article #123", "Brand guideline v2.1"],
  "variants": [
    {"id": "V1", "subject": "Hi Emma...", "body": "Dear Emma..."},
    {"id": "V2", "subject": "Emma, don't miss...", "body": "Hello Emma..."}
  ],
  "safety": {
    "safe": [{"id": "V1", "subject": "Hi Emma...", "body": "Dear Emma..."}],
    "blocked": [{"id": "V2", "reason": "policy_violation"}]
  },
  "analysis": {"winner": {"variant_id": "V1", "score": 0.87}},
  "delivery": {"status": "sent", "message_id": "msg_abc123"}
}
```

---

## Notes & recommendations

- These endpoints are for development and debugging only. Disable in production by not setting `ECHO_DEBUG`.
- **GET /debug/deliveries**: Use `mock=true` for fast UI iteration. Use without `mock` to test actual pipeline.
- **POST /debug/run**: Inspect complete pipeline execution including all intermediate stages.
- The `body_text` field in `/debug/deliveries` is a compatibility alias for `body`.
- Consider using `ECHO_DEBUG_CACHE_TTL` for caching to speed up UI development.

That's it — let me know if you'd like me to add this snippet into the repo's root `README.md` as well or create a short example component that fetches and renders the previews.