import csv

def to_bool(value):
    if value is None:
        return False
    s = str(value).strip().lower()
    return s in ["yes", "y", "true", "1"]

def prettify_slug(value):
    if not value:
        return "Unknown"
    return value.replace("-", " ").replace("_", " ").title()


def segment_user(customer: dict) -> dict:
    """
    customer example:
    {
      "user_id": "U001",
      "email": "a@example.com",
      "viewed_page": "payment_plans",
      "form_started": "yes",
      "scheduled": "no",
      "attended": "no",
    }
    """

    # Opt-in instrumentation (no-op when disabled)
    try:
        from services.langsmith_monitor import start_run, log_event, finish_run, LANGSMITH_ENABLED
    except Exception:
        start_run = log_event = finish_run = lambda *a, **k: None
        LANGSMITH_ENABLED = False

    run_id = None
    if LANGSMITH_ENABLED:
        run_id = start_run("segmenter.segment_user", {"user_id": customer.get("user_id"), "email": customer.get("email")})

    viewed_page = (customer.get("viewed_page") or "").strip().lower()
    form_started = to_bool(customer.get("form_started"))
    scheduled = to_bool(customer.get("scheduled"))
    attended = to_bool(customer.get("attended"))

    use_case = viewed_page or "unknown"
    use_case_label = prettify_slug(use_case)

    if attended:
        funnel_stage = "CompletedScheduledStep"
        intent_level = "very_high"
        reasons = [
            "completed a scheduled step (call/session/meeting)",
            "shows very strong commitment",
        ]
    elif scheduled:
        funnel_stage = "ScheduledNextStep"
        intent_level = "high"
        reasons = [
            "scheduled a next step but has not completed it yet",
            "shows strong intent",
        ]
    elif form_started:
        funnel_stage = "StartedFormOrFlow"
        intent_level = "medium"
        reasons = [
            "started a form or flow but did not finish",
            "shows interest and may need a nudge",
        ]
    else:
        funnel_stage = "BrowsingOnly"
        intent_level = "low"
        reasons = [
            "viewed a page but did not start the flow",
            "early-stage interest",
        ]

    segment_label = f"{use_case}:{funnel_stage}"
    reasons.insert(0, f"interested in: {use_case_label}")

    result = {
        "segment": segment_label,
        "use_case": use_case,
        "use_case_label": use_case_label,
        "funnel_stage": funnel_stage,
        "intent_level": intent_level,
        "reasons": reasons,
    }

    if run_id:
        try:
            log_event(run_id, "segment_computed", {"segment": segment_label, "intent_level": intent_level})
            finish_run(run_id, status="success", outputs={"segment": segment_label})
        except Exception:
            try:
                finish_run(run_id, status="error", outputs={})
            except Exception:
                pass

    return result


def load_customers_from_csv(csv_path: str):
    customers = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            customers.append(row)
    return customers
if __name__ == "__main__":
    """
    Quick manual test for the segmenter.

    Run with:
        cd backend
        python -m agents.segmenter
    """

    from pathlib import Path

    # Go from backend/agents/segmenter.py -> backend/ -> project root -> data/
    project_root = Path(__file__).resolve().parents[2]
    csv_path = project_root / "data" / "customer_events.csv"

    print(f"Loading customers from: {csv_path}")

    customers = load_customers_from_csv(str(csv_path))

    for customer in customers:
        seg = segment_user(customer)
        print("-" * 50)
        print("User:", customer.get("user_id"), customer.get("email"))
        print("Viewed page:", customer.get("viewed_page"))
        print("Segment label:", seg["segment"])
        print("Funnel stage:", seg["funnel_stage"])
        print("Intent level:", seg["intent_level"])
        print("Reasons:")
        for r in seg["reasons"]:
            print("  -", r)
