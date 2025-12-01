# backend/app/nodes/hitl_node.py

from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import uuid4

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
    - In a future step, you can persist this in a database/Redis/queue
      and build API endpoints like:
        - GET /hitl/{review_id}
        - POST /hitl/decide  (approve/reject)
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

        hitl_payload = {
            "review_id": review_id,
            "status": "pending_human_approval",
            "customer_id": customer.get("id"),
            "email": customer.get("email"),
            "num_variants": len(variants),
        }

        # In a real system, you might persist (customer + variants)
        # keyed by review_id in a DB or Redis here.
        # For now, we only log it so you can see it in the logs.
        self.logger.info(
            "HITLNode: created review job %s for customer %s with %d variants",
            review_id,
            customer.get("id") or customer.get("email"),
            len(variants),
        )

        return hitl_payload
