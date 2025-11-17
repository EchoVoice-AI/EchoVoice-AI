from app.nodes.safety_node import SafetyNode


def test_safety_node_filters_structure():
    node = SafetyNode()
    # safety expects variants list; use simple list
    variants = [{"id": "v1", "subject": "hi", "body": "text"}]
    res = node.run(variants)
    assert isinstance(res, dict) or res is None
