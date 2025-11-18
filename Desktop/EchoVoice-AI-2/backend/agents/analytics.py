import random

def evaluate_variants(variants: list, customer: dict) -> dict:
    # Mock evaluation: assign random CTR estimates and pick best
    results = []
    for v in variants:
        ctr = round(random.uniform(0.02, 0.20), 3)
        results.append({'variant_id': v.get('id'), 'ctr': ctr})
    winner = max(results, key=lambda r: r['ctr']) if results else None
    return {'results': results, 'winner': winner}
