# backend/tests/test_hitl_router.py

from fastapi.testclient import TestClient

from app.main import app
from app.store import reviews as review_store

client = TestClient(app)


def _create_sample_review(review_id: str = "review_test_1"):
    customer = {"id": "cust_123", "email": "test@example.com"}
    variants = [
        {"id": "A", "text": "Hello A"},
        {"id": "B", "text": "Hello B"},
    ]
    review_store.create_review(review_id, customer, variants)
    return review_id


def test_get_hitl_review_success():
    review_id = _create_sample_review("review_get_ok")

    resp = client.get(f"/hitl/{review_id}")
    assert resp.status_code == 200

    data = resp.json()
    assert data["review_id"] == review_id
    assert data["status"] == "pending_human_approval"
    assert data["customer"]["id"] == "cust_123"
    assert len(data["variants"]) == 2


def test_get_hitl_review_not_found():
    resp = client.get("/hitl/nonexistent_review")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Review not found"


def test_submit_hitl_decision_updates_review():
    review_id = _create_sample_review("review_decision_ok")

    payload = {
        "approved_variant_id": "A",
        "notes": "Looks good to send",
    }

    resp = client.post(f"/hitl/{review_id}/decision", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    assert data["review_id"] == review_id
    assert data["status"] == "approved"
    assert data["approved_variant_id"] == "A"
    assert data["notes"] == "Looks good to send"

    # Double-check store state
    stored = review_store.get_review(review_id)
    assert stored["status"] == "approved"
    assert stored["approved_variant_id"] == "A"
    assert stored["notes"] == "Looks good to send"
