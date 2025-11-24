"""Selector for experiments/variants (placeholder)."""

def select_variant(user_context: dict, variants: list) -> str:
    """Select an experiment variant based on user context."""
    return variants[0] if variants else "default"
