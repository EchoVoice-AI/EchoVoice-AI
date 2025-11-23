from app.graph.langgraph_flow import build_graph


def test_langgraph_delivery_smoke():
    graph = build_graph()
    test_customer = {
        "id": "U_TEST",
        "email": "test@example.com",
        "last_event": "payment_plans",
        "properties": {"form_started": "yes"},
    }
    final = graph.invoke({"customer": test_customer})
    assert "delivery" in final
    delivery = final.get("delivery")
    assert delivery and delivery.get("status") == "sent"
