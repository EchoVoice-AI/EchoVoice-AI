from app.nodes.segmenter_node import SegmenterNode


def test_segmenter_node_run_shape():
    node = SegmenterNode()
    customer = {"viewed_page": "pricing", "form_started": "yes"}
    result = node.run(customer)
    assert isinstance(result, dict)
    assert "segment" in result
    assert "funnel_stage" in result
