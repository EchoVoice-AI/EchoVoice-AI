from app.nodes.generator_node import GeneratorNode


def test_generator_node_returns_list():
    node = GeneratorNode()
    payload = {
        "customer": {"user_id": "U1"},
        "segment": "unknown",
        "citations": [],
    }
    res = node.run(payload)
    assert isinstance(res, list) or res is None
