from app.nodes.retriever_node import RetrieverNode


def test_retriever_node_returns_list_or_iterable():
    node = RetrieverNode()
    # minimal customer
    customer = {"user_id": "U1"}
    res = node.run(customer)
    assert hasattr(res, "__iter__") or res is None
