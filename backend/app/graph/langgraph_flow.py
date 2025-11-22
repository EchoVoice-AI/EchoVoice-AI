from typing import TypedDict, Dict, Any, List
import os
import logging

from langgraph.graph import StateGraph, END

from app.nodes.segmenter_node import SegmenterNode
from app.nodes.retriever_node import RetrieverNode
from app.nodes.generator_node import GeneratorNode
from app.nodes.safety_node import SafetyNode
from app.nodes.analytics_node import AnalyticsNode
from app.nodes.hitl_node import HITLNode  
from services.delivery import send_email_mock

try:
    from services.email_acs import send_email_acs
except ImportError:
    send_email_acs = None

logger = logging.getLogger(__name__)


class FlowState(TypedDict, total=False):
    """
    Shared state that flows between nodes in the LangGraph graph.
    """
    customer: Dict[str, Any]
    segment: Dict[str, Any]
    citations: List[Dict[str, Any]]
    variants: List[Dict[str, Any]]
    safety: Dict[str, Any]
    hitl: Dict[str, Any]
    analysis: Dict[str, Any]
    delivery: Dict[str, Any]


# -----------------------
# Node wrapper functions
# -----------------------


def segmenter_node(state: FlowState) -> FlowState:
    customer = state["customer"]
    properties = customer.get("properties") or {}

    segmenter_customer = {
        "user_id": customer.get("id"),
        "email": customer.get("email"),
        "viewed_page": customer.get("last_event"),   
        "form_started": properties.get("form_started"),
        "scheduled": properties.get("scheduled"),
        "attended": properties.get("attended"),
    }

    segment = SegmenterNode().run(segmenter_customer)
    state["segment"] = segment
    return state


def retriever_node(state: FlowState) -> FlowState:
    """
    Retrieve citations / knowledge snippets for the given customer/segment.
    """
    citations = RetrieverNode().run(state["customer"])
    state["citations"] = citations
    return state


def generator_node(state: FlowState) -> FlowState:
    """
    Generate message variants using customer, segment, and citations.
    """
    variants = GeneratorNode().run(
        {
            "customer": state["customer"],
            "segment": state["segment"],
            "citations": state["citations"],
        }
    )
    state["variants"] = variants
    return state


def safety_node(state: FlowState) -> FlowState:
    """
    Run the safety gate on generated variants.
    Returns {"safe": [...], "blocked": [...]}.
    """
    safety_result = SafetyNode().run(state["variants"])
    state["safety"] = safety_result
    return state


def hitl_node(state: FlowState) -> FlowState:
    """
    Human-in-the-loop (HITL) node.

    Takes the safe variants from the safety gate and enqueues them
    for human review. For now, we still continue the flow (analytics
    + delivery), but in a stricter RAI mode you could stop here and
    wait for human approval.
    """
    safety_result = state.get("safety") or {}
    safe_variants: List[Dict[str, Any]] = safety_result.get("safe", [])

    hitl_result = HITLNode().run(state["customer"], safe_variants)
    # Example hitl_result: {"review_id": "...", "status": "pending_human_approval"}
    state["hitl"] = hitl_result
    return state


def analytics_node(state: FlowState) -> FlowState:
    """
    Analytics node.

    Scores safe variants (e.g., mock CTRs) and chooses a winner.
    """
    safety_result = state.get("safety") or {}
    safe_variants: List[Dict[str, Any]] = safety_result.get("safe", [])

    if not safe_variants:
        state["analysis"] = {"results": [], "winner": None}
        return state

    analysis = AnalyticsNode().run(
        {
            "variants": safe_variants,
            "customer": state["customer"],
        }
    )
    state["analysis"] = analysis
    return state


def delivery_node(state: FlowState) -> FlowState:
    """
    Delivery node.

    Looks at the analytics winner and sends the corresponding variant via:
    1. Azure Communication Services (ACS) EmailClient if configured and available
    2. Falls back to mock delivery service for development/testing
    """
    analysis = state.get("analysis") or {}
    winner = analysis.get("winner")
    safety_result = state.get("safety") or {}
    safe_variants: List[Dict[str, Any]] = safety_result.get("safe", [])

    if not winner or not safe_variants:
        state["delivery"] = None
        return state

    # Find the winning variant
    winner_id = winner.get("variant_id")
    variant = next(
        (v for v in safe_variants if v.get("id") == winner_id),
        None,
    )

    if not variant:
        state["delivery"] = None
        return state

    # Extract email details
    email = state["customer"].get("email")
    subject = variant.get("subject")
    body = variant.get("body")

    # Try ACS email delivery first if available
    delivery_result = None
    if send_email_acs is not None:
        try:
            use_acs = os.getenv("USE_ACS_EMAIL", "false").lower() == "true"
            if use_acs:
                logger.info(f"[delivery] Sending email via Azure Communication Services to {email}")
                delivery_result = send_email_acs(email, subject, body)
                delivery_result["service"] = "acs"
            else:
                logger.debug("[delivery] ACS email disabled, using mock service")
                delivery_result = send_email_mock(email, subject, body)
                delivery_result["service"] = "mock"
        except Exception as e:
            logger.error(f"[delivery] ACS email failed: {e}. Falling back to mock service.")
            delivery_result = send_email_mock(email, subject, body)
            delivery_result["service"] = "mock"
    else:
        logger.debug("[delivery] ACS email not available, using mock service")
        delivery_result = send_email_mock(email, subject, body)
        delivery_result["service"] = "mock"

    state["delivery"] = delivery_result
    return state


# -----------------------
# Graph builder
# -----------------------


def build_graph():
    """
    Build and compile the LangGraph StateGraph that represents
    the full mini-agent pipeline:

        segmenter -> retriever -> generator -> safety
                  -> hitl -> analytics -> delivery -> END
    """
    graph = StateGraph(FlowState)

    # Register nodes
    graph.add_node("segmenter", segmenter_node)
    graph.add_node("retriever", retriever_node)
    graph.add_node("generator", generator_node)
    graph.add_node("safety", safety_node)
    graph.add_node("hitl", hitl_node)
    graph.add_node("analytics", analytics_node)
    graph.add_node("delivery", delivery_node)

    # Wire edges
    graph.set_entry_point("segmenter")
    graph.add_edge("segmenter", "retriever")
    graph.add_edge("retriever", "generator")
    graph.add_edge("generator", "safety")
    graph.add_edge("safety", "hitl")
    graph.add_edge("hitl", "analytics")
    graph.add_edge("analytics", "delivery")
    graph.add_edge("delivery", END)

    return graph.compile()
if __name__ == "__main__":
    """
    Manual smoke test for the LangGraph flow.

    Run with:
        cd backend
        python -m app.graph.langgraph_flow
    """
    import json

    graph = build_graph()

    test_customer = {
        "id": "U_TEST",
        "email": "test@example.com",
        "last_event": "payment_plans",
        "properties": {
            "form_started": "yes",
            "scheduled": "no",
            "attended": "no",
        },
    }

    initial_state = {"customer": test_customer}
    final_state = graph.invoke(initial_state)

    print("=== LangGraph flow final state ===")
    print(json.dumps(final_state, indent=2))

