"""Selector for experiments/variants (placeholder)."""
from typing import Any, Dict, List


def select_variant(user_context: Dict[str, Any], variants: List[str]) -> str:
    """Simulate variant selection (e.g., Round-Robin, Multi-Armed Bandit).
    
    The 'experimentation_node' uses this to decide which message to send.
    """
    # Simple placeholder: always picks the first available variant
    return variants[0] if variants else "A"