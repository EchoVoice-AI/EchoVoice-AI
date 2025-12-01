import pytest

from agents.delivery_agent import deliver_for_user


def test_deliver_for_user_sends_winner():
    ctx = {
        "customer": {"id": "u_test", "email": "ci@example.com"},
        "safety": {"safe": [
            {"id": "v_a", "subject": "Sub A", "body": "Body A"},
            {"id": "v_b", "subject": "Sub B", "body": "Body B"},
        ]},
        "analysis": {"winner": {"variant_id": "v_b"}},
    }

    result = deliver_for_user(ctx)
    assert isinstance(result, dict)
    assert result.get("status") in ("sent", "dry_run")
    # when not dry_run, ensure variant_id matches
    if result.get("status") == "sent":
        assert result.get("variant_id") == "v_b"


def test_deliver_for_user_no_customer():
    result = deliver_for_user({})
    assert result.get("status") == "no_customer"
