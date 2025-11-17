from services.vector_db import simple_lookup_by_product_id

def retrieve_citations(customer: dict) -> list:
    # Example: fetch the product doc for the product_id in customer properties
    props = customer.get('properties', {})
    pid = props.get('product_id')
    if not pid:
        return []
    doc = simple_lookup_by_product_id(pid)
    if not doc:
        return []
    return [{
        'id': doc.get('id'),
        'title': doc.get('title'),
        'content': doc.get('content'),
        'source': doc.get('source')
    }]
