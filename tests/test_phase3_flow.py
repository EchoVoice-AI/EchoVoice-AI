import json
import pytest
from types import SimpleNamespace

from PersonalizeAI.nodes.phase3_generation import (
    ai_message_generator,
    compliance_agent,
    rewrite_decision,
    automated_rewrite,
)


class FakeOpenAI:
    def __init__(self, responses):
        # responses: list of JSON strings to return in sequence
        self._responses = list(responses)
        self.chat = SimpleNamespace()

        async def create(*args, **kwargs):
            if not self._responses:
                return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=""))])
            content = self._responses.pop(0)
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])

        self.chat.completions = SimpleNamespace(create=create)


@pytest.mark.asyncio
async def test_phase3_compliance_loop_with_llm():
    # Prepare ordered LLM responses: generator, judge A/B/C, rewrite, judge A/B/C recheck
    generator_output = json.dumps([
        {"id": "A", "subject": "S1", "body": "Safe body A", "cta": "CTA A"},
        {"id": "B", "subject": "S2", "body": "Your loyalty is valued... ensuring you meet your fitness goals.", "cta": "CTA B"},
        {"id": "C", "subject": "S3", "body": "Safe body C", "cta": "CTA C"},
    ])

    judge_A1 = json.dumps({"is_compliant": True, "reason": None})
    judge_B1 = json.dumps({"is_compliant": False, "reason": "Health claim ('fitness goals') detected."})
    judge_C1 = json.dumps({"is_compliant": True, "reason": None})

    rewrite_B = json.dumps({"id": "B", "subject": "S2", "body": "Your loyalty is valued... supporting your active lifestyle.", "cta": "CTA B"})

    judge_A2 = json.dumps({"is_compliant": True, "reason": None})
    judge_B2 = json.dumps({"is_compliant": True, "reason": None})
    judge_C2 = json.dumps({"is_compliant": True, "reason": None})

    responses = [generator_output, judge_A1, judge_B1, judge_C1, rewrite_B, judge_A2, judge_B2, judge_C2]

    fake_openai = FakeOpenAI(responses)

    state = {
        "segment_description": "High value shoppers",
        "retrieved_content": [{"text": "Fact 1"}],
    }

    # Step 1: generate
    gen_update = await ai_message_generator.ai_message_generator(state, openai_client=fake_openai, prompt_manager=None, approach=None)
    assert "message_variants" in gen_update
    state.update(gen_update)
    assert len(state["message_variants"]) == 3

    # Step 2: compliance + possible rewrite loop
    comp_update = await compliance_agent.compliance_agent(state, openai_client=fake_openai, prompt_manager=None, approach=None)
    state.update(comp_update)

    # After first compliance check, variant B should be non-compliant
    non_compliant = [e for e in state["compliance_log"] if not e["is_compliant"]]
    assert any(e["variant_id"] == "B" for e in non_compliant)

    # Decision should request an automated rewrite
    route = rewrite_decision.rewrite_decision(state)
    assert route == "AUTOMATED_REWRITE"

    # Perform rewrite
    rewrite_update = await automated_rewrite.automated_rewrite(state, openai_client=fake_openai, prompt_manager=None, approach=None)
    state.update(rewrite_update)

    # After rewrite, B's body should be updated
    b_variant = next(v for v in state["message_variants"] if v["id"] == "B")
    assert "supporting your active lifestyle" in b_variant["body"]

    # Re-run compliance
    comp_update2 = await compliance_agent.compliance_agent(state, openai_client=fake_openai, prompt_manager=None, approach=None)
    state.update(comp_update2)

    # All variants should now be compliant
    assert all(e["is_compliant"] for e in state["compliance_log"][-3:])
