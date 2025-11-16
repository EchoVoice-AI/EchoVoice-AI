from ..app.config import LOG_LEVEL

PROHIBITED_TERMS = ["cure", "guarantee of cure"]

def safety_check_and_filter(variants: list) -> dict:
    safe = []
    blocked = []
    for v in variants:
        body = v.get('body', '').lower()
        if any(term in body for term in PROHIBITED_TERMS):
            blocked.append({'variant': v, 'reason': 'prohibited_term'})
        else:
            safe.append(v)
    return {'safe': safe, 'blocked': blocked}
