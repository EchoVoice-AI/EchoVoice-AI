from typing import Any

from .base_node import BaseNode
from agents.segmenter import segment_user


class SegmenterNode(BaseNode):
    """Node wrapper around the `segment_user` utility.

    This allows the segmenter to be used as a pluggable node in the
    orchestrator graph while sharing a consistent interface (`run`).
    """

    def __init__(self, name: str = "segmenter"):
        super().__init__(name)

    def run(self, data: Any) -> dict:
        """Run segmentation on `data` (expected dict-like customer).

        Returns the segment dict produced by `agents.segmenter.segment_user`.
        """
        return segment_user(data)


if __name__ == "__main__":
    # Quick manual smoke test
    sample = {"viewed_page": "pricing", "form_started": "yes"}
    node = SegmenterNode()
    print(node.run(sample))
