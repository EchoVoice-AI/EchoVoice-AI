from agents.delivery_agent import DeliveryAgent


def test_delivery_agent_fallback():
    agent = DeliveryAgent()
    res = agent.deliver("test@example.com", "Hi", "body")
    assert isinstance(res, dict)
    assert res.get("status") == "sent"
