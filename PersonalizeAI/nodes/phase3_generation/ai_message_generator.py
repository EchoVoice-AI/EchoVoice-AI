from typing import Dict, List, Any, Optional
from PersonalizeAI.state import GraphState
import json
import logging
from pathlib import Path
from PersonalizeAI.utils.response_cleaner import parse_and_validate_generator


async def ai_message_generator(
    state: GraphState,
    openai_client: Optional[Any] = None,
    prompt_manager: Optional[Any] = None,
    approach: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Generates multiple personalized message variants using an LLM when
    `openai_client` is provided. Falls back to a deterministic set when no
    client is available.
    """
    segment_desc = state.get("segment_description", "")
    retrieved = state.get("retrieved_content", []) or []

    context = "\n".join([c.get("text", "") for c in retrieved])

    model_to_use = None
    try:
        if approach is not None:
            model_to_use = getattr(approach, "chatgpt_deployment", None) or getattr(approach, "chatgpt_model", None)
    except Exception:
        model_to_use = None

    # If we have an OpenAI-like client, attempt an LLM generation
    if openai_client is not None:
        messages = None
        if prompt_manager is not None:
            try:
                prompt = prompt_manager.load_prompt("phase3_generation/ai_message_generator.prompty")
                messages = prompt_manager.render_prompt(prompt, {"segment_description": segment_desc, "context": context})
            except Exception:
                messages = None

        if messages is None:
            # Build a simple instruction-based prompt
            messages = [
                {"role": "system", "content": "You are a concise marketing copywriter. Generate 3 unique message variants with id A, B, C. Include subject, body, and cta for each variant. Keep content grounded in the provided context and include inline citations where available."},
                {"role": "user", "content": f"Segment: {segment_desc}\nContext:\n{context}\nRespond in JSON: [{'{'}\"id\":\"A\",\"subject\":\"...\",\"body\":\"...\",\"cta\":\"...\"{'}'}, ...]"},
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
                    parsed = parse_and_validate_generator(content)
                    return {"message_variants": parsed}
                except Exception as exc:
                    logging.getLogger("phase3.generator").exception("Failed to parse generator output: %s", exc)
                    # naive fallback: put the whole content into a single variant
                    return {"message_variants": [{"id": "A", "subject": segment_desc[:60], "body": content, "cta": "Learn More"}]}
        except Exception:
            pass

    # Deterministic fallback
    variants: List[Dict[str, str]] = [
        {
            "id": "A",
            "subject": "Boost Your Day: 20g Protein, Zero Sugar!",
            "body": "As a health-conscious shopper, try our new protein bar! It delivers a full 20g of high-quality whey protein and zero added sugar.",
            "cta": "Shop New Bars",
        },
        {
            "id": "B",
            "subject": "High-Value Offer: Protein Bar Inside",
            "body": "Your loyalty is valued. We know you seek quality, so here's a limited offer on our high-quality whey protein bar, ensuring you meet your fitness goals.",
            "cta": "Get Discount",
        },
        {
            "id": "C",
            "subject": "Try The New Protein Bar — Tastes Great",
            "body": "New arrival: a protein bar made with high-quality whey and natural flavors. Perfect as a post-workout snack.",
            "cta": "Learn More",
        },
    ]

    return {"message_variants": variants}
