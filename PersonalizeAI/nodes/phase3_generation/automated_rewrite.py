from typing import Dict, List, Any, Optional
from PersonalizeAI.state import GraphState
import json
import logging
from PersonalizeAI.utils.response_cleaner import parse_and_validate_rewrite


async def automated_rewrite(
    state: GraphState,
    openai_client: Optional[Any] = None,
    prompt_manager: Optional[Any] = None,
    approach: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Rewrites non-compliant message variants. If `openai_client` is available,
    use the LLM to produce a compliant rewrite; otherwise apply simple
    deterministic replacements.
    """
    variants = state.get("message_variants", []) or []
    compliance_log = state.get("compliance_log", []) or []

    non_compliant_ids = {log["variant_id"] for log in compliance_log if not log.get("is_compliant")}

    updated_variants: List[Dict[str, str]] = []

    model_to_use = None
    try:
        if approach is not None:
            model_to_use = getattr(approach, "chatgpt_deployment", None) or getattr(approach, "chatgpt_model", None)
    except Exception:
        model_to_use = None

    for variant in variants:
        vid = variant.get("id")
        if vid in non_compliant_ids:
            reason = next((log.get("reason") for log in reversed(compliance_log) if log.get("variant_id") == vid and not log.get("is_compliant")), "Policy violation.")

            # Prefer LLM-based rewrite when available
            if openai_client is not None:
                messages = None
                if prompt_manager is not None:
                    try:
                        pm_prompt = prompt_manager.load_prompt("phase3_generation/automated_rewrite.prompty")
                        messages = prompt_manager.render_prompt(pm_prompt, {"variant": variant, "reason": reason})
                    except Exception:
                        messages = None

                if messages is None:
                    messages = [
                        {"role": "system", "content": "You are a constrained rewrite assistant. Given a message variant and a reason it failed policy, produce a rewritten variant that preserves core meaning but removes/mitigates the violation. Respond with JSON: {\"id\":..., \"subject\":..., \"body\":..., \"cta\":...}"},
                        {"role": "user", "content": f"Reason: {reason}\nOriginal: {variant}"},
                    ]

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
                                parsed = parse_and_validate_rewrite(content)
                                if isinstance(parsed, dict):
                                    variant.update(parsed)
                                    print(f"Variant {vid} rewritten by LLM.")
                            except Exception as exc:
                                logging.getLogger("phase3.rewrite").exception("Failed to parse rewrite output: %s", exc)
                                # fallback to simple replacement if LLM returned free text
                                if "fitness goals" in variant.get("body", "").lower():
                                    variant["body"] = variant.get("body", "").replace("ensuring you meet your fitness goals.", "supporting your active lifestyle.")
                except Exception:
                    # LLM failed; fall back to deterministic
                    if "fitness goals" in variant.get("body", "").lower():
                        variant["body"] = variant.get("body", "").replace("ensuring you meet your fitness goals.", "supporting your active lifestyle.")

            else:
                # deterministic rewrite
                if "fitness goals" in variant.get("body", "").lower():
                    variant["body"] = variant.get("body", "").replace("ensuring you meet your fitness goals.", "supporting your active lifestyle.")

        updated_variants.append(variant)

    return {"message_variants": updated_variants}
