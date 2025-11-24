# backend/tests/test_audit_log.py

from app.store import audit_log
from app.store import store


def test_log_action_creates_and_appends_entries():
    review_id = "review_test_1"

    # Make sure we start clean for this key
    store.set(f"hitl:log:{review_id}", None)

    # Log first action
    audit_log.log_action(
        review_id=review_id,
        action="TTS_PLAY",
        user_id="selvi",
        metadata={"variant_id": "A"},
    )

    # Log second action
    audit_log.log_action(
        review_id=review_id,
        action="TRANSLATE",
        user_id="selvi",
        metadata={"target_lang": "es"},
    )

    logs = audit_log.get_logs(review_id)

    assert len(logs) == 2

    first, second = logs[0], logs[1]

    # First entry
    assert first["review_id"] == review_id
    assert first["user_id"] == "selvi"
    assert first["action"] == "TTS_PLAY"
    assert first["metadata"]["variant_id"] == "A"
    assert "timestamp" in first

    # Second entry
    assert second["review_id"] == review_id
    assert second["user_id"] == "selvi"
    assert second["action"] == "TRANSLATE"
    assert second["metadata"]["target_lang"] == "es"
    assert "timestamp" in second


def test_get_logs_returns_empty_list_when_no_logs():
    review_id = "review_no_logs"

    # Ensure nothing stored for this key
    store.set(f"hitl:log:{review_id}", None)

    logs = audit_log.get_logs(review_id)

    assert isinstance(logs, list)
    assert logs == []


def test_log_action_skips_when_review_id_is_none():
    # If review_id is None, we currently no-op.
    audit_log.log_action(
        review_id=None,
        action="TTS_PLAY",
        user_id="someone",
        metadata={"foo": "bar"},
    )

    # There is no specific key to check; we just assert that it doesn't crash.
    # If you want stricter behavior later, you can change log_action and update this test.
