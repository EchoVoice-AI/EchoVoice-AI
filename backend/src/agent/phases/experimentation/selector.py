"""Selector for experiments/variants (placeholder)"""

def select_variant(user_context: dict, variants: list) -> str:
    return variants[0] if variants else "default"
