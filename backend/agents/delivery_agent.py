"""Delivery agent

This module provides a small delivery agent that the orchestrator can call to
perform (mock) delivery of a winning variant to a user. The implementation is
kept simple and stateless so it can later be extended to use Azure services
(SendGrid, Event Grid, Service Bus) when you deploy.

Contract (expected keys in `context`):
- customer: dict with at least 'email' (and optionally 'id', 'name')
- safety: dict with key 'safe' -> list of variant dicts (each variant may have 'id','subject','body')
- analysis: dict which may contain 'winner' with field 'variant_id'
- options: optional dict, supports 'dry_run' (True -> do not actually call delivery)

Functions:
- deliver_for_user(context: dict) -> dict
    Attempts to send the winner variant if present. Returns a dict describing
    the delivery outcome.
"""

from typing import Dict, Any, List, Optional

try:
    # project uses a services module for delivery and logging
    from services.delivery import send_email_mock
    from services.logger import get_logger
except Exception:
    # Safe fallbacks for editing/testing outside the full project layout
    def send_email_mock(to_email: str, subject: str, body: str):
        print(f"[delivery_mock] to={to_email} subject={subject}\n{body}\n---")
        return {"status": "sent", "to": to_email}

    def get_logger(name: str):
        class _Logger:
            def info(self, *a, **k):
                print("INFO:", *a)

            def warning(self, *a, **k):
                print("WARN:", *a)

            def error(self, *a, **k):
                print("ERROR:", *a)

            def exception(self, *a, **k):
                print("EXCEPTION:", *a)

        return _Logger()


logger = get_logger("delivery_agent")


def _find_winner_variant(safe_variants: List[Dict[str, Any]], analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    # analysis may contain {'winner': {'variant_id': '...'}} or similar
    if not analysis:
        return None

    winner = analysis.get("winner")
    if not winner:
        return None

    variant_id = winner.get("variant_id") or winner.get("id") or winner.get("variant")
    if not variant_id:
        return None

    return next((v for v in safe_variants if v.get("id") == variant_id), None)


def deliver_for_user(context: Dict[str, Any]) -> Dict[str, Any]:
    """Deliver the winning variant (mock) for a single user.

    Returns a result dict with keys like 'status' and details in 'result'.
    """
    customer = context.get("customer") or context.get("payload")
    if not customer:
        logger.error("No customer in context; skipping delivery")
        return {"status": "no_customer"}

    to_email = customer.get("email")
    if not to_email:
        logger.warning("Customer missing email; skipping delivery", customer)
        return {"status": "no_recipient", "customer": customer}

    # Determine safe variants
    safety = context.get("safety") or {}
    safe_variants: List[Dict[str, Any]] = safety.get("safe") if isinstance(safety, dict) else None
    if safe_variants is None:
        # fallback to 'variants' if safety not provided
        safe_variants = context.get("variants") or []

    analysis = context.get("analysis") or {}
    options = context.get("options") or {}
    dry_run = bool(options.get("dry_run"))

    # Find winner
    winner_variant = _find_winner_variant(safe_variants, analysis)
    if not winner_variant:
        logger.info("No winner found for customer; nothing to deliver", customer.get("id"))
        return {"status": "no_winner"}

    variant_id = winner_variant.get("id")
    subject = winner_variant.get("subject", "")
    body = winner_variant.get("body", "")

    # Respect dry-run option
    if dry_run:
        logger.info("Dry run delivery", to_email, variant_id)
        return {"status": "dry_run", "to": to_email, "variant_id": variant_id}

    try:
        delivery_resp = send_email_mock(to_email, subject, body)
        logger.info("Delivered variant", variant_id, "to", to_email)
        return {"status": "sent", "variant_id": variant_id, "delivery": delivery_resp}
    except Exception as exc:
        logger.exception("Delivery failed for %s", to_email)
        return {"status": "error", "error": str(exc)}


if __name__ == "__main__":
    # quick manual smoke test when executed in isolation
    sample_context = {
        "customer": {"id": "u1", "email": "test@example.com"},
        "safety": {"safe": [{"id": "v1", "subject": "Hello", "body": "This is a test."}]},
        "analysis": {"winner": {"variant_id": "v1"}},
    }
    print(deliver_for_user(sample_context))
