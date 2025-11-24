# Backend - Debug Previews Endpoint

This short snippet documents the debug endpoint that runs the personalization pipeline and returns only the email preview outputs for UI previewing.

## Endpoint

- Path: `GET /debug/deliveries`
- Purpose: Run the orchestrator for a small set of mock customers and return minimal email preview objects (subject and body) that the frontend can use for UI preview.
- Dev-only: This router is mounted only when the `ECHO_DEBUG` environment variable is set to `1`, `true`, or `yes`.

## Query parameters

- `mock` (optional, boolean): When `true`, the endpoint returns a precomputed set of lightweight previews without running the pipeline. Useful for fast UI design.

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

2. Hit the endpoint (mock):

```powershell
curl "http://127.0.0.1:8000/debug/deliveries?mock=true"
```

3. Hit the endpoint (run pipeline):

```powershell
curl "http://127.0.0.1:8000/debug/deliveries"
```

## Notes & recommendations

- This endpoint is intended for development / UI preview only. Keep it disabled in production by not setting `ECHO_DEBUG`.
- Use `mock=true` for fast, deterministic previews while designing UI components.
- If the frontend expects a different key name (for example `body_text`), either adapt the frontend or add the compatibility key in the preview object.
- For heavy real nodes, consider adding caching or a TTL so UI previews are fast and deterministic.

That's it — let me know if you'd like me to add this snippet into the repo's root `README.md` as well or create a short example component that fetches and renders the previews.