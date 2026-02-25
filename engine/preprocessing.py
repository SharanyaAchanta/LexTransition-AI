def preprocess_query(query: str) -> str:
    """
    Basic query preprocessing:
    - Lowercases text
    - Strips extra whitespace
    """
    if not query:
        return ""

    query = query.lower().strip()
    return query