from typing import Dict, List, Any
from PersonalizeAI.state import GraphState
from typing import Dict, List, Any, Optional
from PersonalizeAI.state import GraphState
from datetime import datetime, timezone
import json
import logging
from PersonalizeAI.utils.response_cleaner import parse_and_validate_judge


# Simplified safety policy rules for demonstration / unit tests
SAFETY_POLICY_RULES = [
    "No medical, health, or body claims without explicit citation.",
    "Do not target sensitive attributes (race, religion, illness, etc.).",
    "Ensure brand tone is positive and motivational.",
]


async def compliance_agent(
    state: GraphState,
    openai_client: Optional[Any] = None,
    prompt_manager: Optional[Any] = None,
    approach: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Evaluate each message variant. If an `openai_client` is provided, use the
    LLM as a judge (prompted to return a compact JSON verdict). Otherwise fall
    back to deterministic keyword checks.
    """
    variants = state.get("message_variants", []) or []
    current_log = state.get("compliance_log", []) or []

    new_compliance_log: List[Dict[str, Any]] = []

    for variant in variants:
        variant_id = variant.get("id")
        body = variant.get("body", "")

        is_compliant = True
        violation_reason = None

        if openai_client is not None:
            # Build a compact judging prompt
            messages = None
            if prompt_manager is not None:
                try:
                    pm_prompt = prompt_manager.load_prompt("phase3_generation/compliance_agent.prompty")
                    messages = prompt_manager.render_prompt(pm_prompt, {"variant": variant, "rules": SAFETY_POLICY_RULES})
                except Exception:
                    messages = None

            if messages is None:
                messages = [
                    {"role": "system", "content": "You are a strict policy judge. For the provided message variant, check it against the rules and respond ONLY with JSON: {\"is_compliant\": true|false, \"reason\": null|\"reason string\"}"},
                    {"role": "user", "content": f"Rules: {SAFETY_POLICY_RULES}\nMessage: {variant}"},
                ]

            model_to_use = None
            try:
                if approach is not None:
                    model_to_use = getattr(approach, "chatgpt_deployment", None) or getattr(approach, "chatgpt_model", None)
            except Exception:
                model_to_use = None

            try:
                if model_to_use:
                    resp = await openai_client.chat.completions.create(model=model_to_use, messages=messages, n=1)
                else:
                    resp = await openai_client.chat.completions.create(messages=messages, n=1)

                content = None
                if resp and getattr(resp, "choices", None):
                    choice = resp.choices[0]
                    if getattr(choice, "message", None) and getattr(choice.message, "content", None):
                        content = choice.message.content.strip()
                    elif getattr(choice, "text", None):
                        content = choice.text.strip()

                if content:
                    try:
                        verdict = parse_and_validate_judge(content)
                        is_compliant = bool(verdict.get("is_compliant", True))
                        violation_reason = verdict.get("reason")
                    except Exception as exc:
                        logging.getLogger("phase3.compliance").exception("Failed to parse judge output: %s", exc)
                        # If parsing fails, fall back to keyword checks below
                        pass
            except Exception:
                # LLM judge failed; fall through to deterministic checks
                pass

        # Deterministic fallback checks
        if violation_reason is None:
            if "fitness goals" in body.lower():
                is_compliant = False
                violation_reason = "Health claim ('fitness goals') detected without explicit product citation."
            if any(word in body.lower() for word in ("race", "religion", "illness")):
                is_compliant = False
                violation_reason = (violation_reason or "Targets sensitive attribute; violates policy.")

        log_entry = {
            "variant_id": variant_id,
            "is_compliant": is_compliant,
            "reason": violation_reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        new_compliance_log.append(log_entry)

        print(f"Variant {variant_id}: {'PASS' if is_compliant else 'FAIL (' + (violation_reason or '') + ')'}")

    state["compliance_log"] = current_log + new_compliance_log
    return {"compliance_log": state["compliance_log"]}
