import re

def normalize_query(query: str) -> str:
    """
    Normalize user query before retrieval:
    - Lowercase conversion
    - Remove unnecessary punctuation
    - Remove extra whitespace
    """

    # Convert to lowercase
    query = query.lower()

    # Remove punctuation (keep alphanumeric and spaces)
    query = re.sub(r"[^\w\s]", "", query)

    # Remove extra whitespace
    query = re.sub(r"\s+", " ", query).strip()

    return query