# backend/tests/test_hitl_review_store.py

from app.nodes.hitl_node import HITLNode
from app.store import reviews as review_store


def test_hitl_node_persists_review_with_variants():
    node = HITLNode()

    customer = {"id": "cust_123", "email": "test@example.com"}
    variants = [
        {"id": "A", "text": "Hello A"},
        {"id": "B", "text": "Hello B"},
    ]

    result = node.run(customer, variants)

    # Check lightweight payload
    assert result["status"] == "pending_human_approval"
    assert result["num_variants"] == 2
    assert result["review_id"] is not None

    review_id = result["review_id"]

    # Check persisted review in store
    stored = review_store.get_review(review_id)
    assert stored is not None
    assert stored["review_id"] == review_id
    assert stored["status"] == "pending_human_approval"
    assert stored["customer"]["id"] == "cust_123"
    assert stored["customer"]["email"] == "test@example.com"
    assert len(stored["variants"]) == 2
    assert stored["approved_variant_id"] is None
    assert stored["notes"] is None
    assert "created_at" in stored
    assert "updated_at" in stored


def test_hitl_node_no_variants_does_not_create_review():
    node = HITLNode()

    customer = {"id": "cust_empty", "email": "empty@example.com"}
    variants = []  # no safe variants

    result = node.run(customer, variants)

    # No review created in this case
    assert result["review_id"] is None
    assert result["status"] == "no_variants"
    assert result["num_variants"] == 0
