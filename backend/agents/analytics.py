import random

def evaluate_variants(variants: list, customer: dict) -> dict:
    # Opt-in instrumentation
    try:
        from services.langsmith_monitor import start_run, log_event, finish_run, LANGSMITH_ENABLED
    except Exception:
        start_run = log_event = finish_run = lambda *a, **k: None
        LANGSMITH_ENABLED = False

    run_id = None
    if LANGSMITH_ENABLED:
        run_id = start_run("analytics.evaluate_variants", {"variant_count": len(variants)})

    # Mock evaluation: assign random CTR estimates and pick best
    results = []
    for v in variants:
        ctr = round(random.uniform(0.02, 0.20), 3)
        results.append({"variant_id": v.get("id"), "ctr": ctr})
    winner = max(results, key=lambda r: r["ctr"]) if results else None

    out = {"results": results, "winner": winner}

    if run_id:
        try:
            log_event(run_id, "evaluation_done", {"winner": winner, "count": len(results)})
            finish_run(run_id, status="success", outputs={"winner": winner})
        except Exception:
            try:
                finish_run(run_id, status="error", outputs={})
            except Exception:
                pass

    return out
