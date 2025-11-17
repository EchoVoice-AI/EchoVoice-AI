from app.nodes.analytics_node import AnalyticsNode


def test_analytics_node_evaluates():
    node = AnalyticsNode()
    variants = [{"id": "v1", "score": 0.5}]
    customer = {"user_id": "U1"}
    res = node.run({"variants": variants, "customer": customer})
    assert isinstance(res, dict) or res is None
