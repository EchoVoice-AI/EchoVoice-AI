# backend/app/nodes/hitl_node.py

from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.store import reviews as review_store #to persist reviews
from services.logger import get_logger


class HITLNode:
    """
    Human-in-the-loop (HITL) review node.

    Responsibility:
    - Take the *safe* variants (already passed the safety gate).
    - Create a lightweight "review job" object with a review_id.
    - Return metadata that the rest of the system can use to:
        * show pending reviews in a UI
        * later record an "approved" or "rejected" decision

    NOTE:
    - This node does NOT block on a human decision.
    - It just prepares the review metadata and logs it.
    - API endpoints like:
        - GET /hitl/{review_id}
        - POST /hitl/{review_id}/decision (approve/reject)
      can load and update the stored review object.
    """

    def __init__(self, logger: Optional[Any] = None) -> None:
        self.logger = logger or get_logger("node.hitl")

    def run(
        self,
        customer: Dict[str, Any],
        variants: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Enqueue variants for human review.

        Args:
            customer: dict with customer info (id, email, etc.)
            variants: list of *safe* variants from the safety gate.

        Returns:
            A dict like:
            {
                "review_id": "review_...",
                "status": "pending_human_approval",
                "customer_id": "...",
                "email": "...",
                "num_variants": 2,
            }
        """
        # If there are no variants, there is nothing to review.
        if not variants:
            result = {
                "review_id": None,
                "status": "no_variants",
                "customer_id": customer.get("id"),
                "email": customer.get("email"),
                "num_variants": 0,
            }
            self.logger.info("HITLNode: no variants to review: %s", result)
            return result

        # Generate a unique review_id that a UI or API can later use
        review_id = f"review_{uuid4().hex}"

        # Persist full HITL review (customer + variants) so it can be fetched later
        # via GET /hitl/{review_id} and updated by POST /hitl/{review_id}/decision.
        # We also log it for traceability / debugging.
        try:
            review_store.create_review(review_id, customer, variants)
        except Exception:
            # If persistence fails, log the error but still return the hitl_payload
            # so the rest of the flow can proceed.
            self.logger.exception(
                "HITLNode: failed to persist review %s to store", review_id
            )

        hitl_payload = {
            "review_id": review_id,
            "status": "pending_human_approval",
            "customer_id": customer.get("id"),
            "email": customer.get("email"),
            "num_variants": len(variants),
        }

        
        self.logger.info(
            "HITLNode: created review job %s for customer %s with %d variants",
            review_id,
            customer.get("id") or customer.get("email"),
            len(variants),
        )

        return hitl_payload
