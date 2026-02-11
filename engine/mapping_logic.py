"""
IPC -> BNS mapping helper with comprehensive mapping database.

Provides exact lookup and fuzzy matching for IPC section numbers/queries
to find their corresponding BNS (Bharatiya Nyaya Sanhita, 2023) equivalents.

The mapping database includes 65+ verified mappings organized by offense categories:
- Offenses Against State
- Offenses Against Public Tranquility  
- Offenses Against Human Body
- Offenses Against Property
- Criminal Breach of Trust & Cheating
- Offenses Against Women
- Offenses Relating to Documents
- And more...

Sources: Ministry of Home Affairs, Official Gazette of India
"""
import os
import json
from difflib import get_close_matches
from typing import Optional, List, Dict

_base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_MAPPING_FILE = os.environ.get("LTA_MAPPING_DB") or os.path.join(_base_dir, "mapping_db.json")

# Fallback mappings if database file is not available
_default_mappings = {
    "420": {"bns_section": "BNS 318", "notes": "Cheating and dishonestly inducing delivery of property", "category": "Cheating", "source": "Official Gazette"},
    "302": {"bns_section": "BNS 103", "notes": "Punishment for murder", "category": "Offenses Against Human Body", "source": "Official Gazette"},
    "378": {"bns_section": "BNS 303", "notes": "Theft - Definition similar", "category": "Offenses Against Property", "source": "Official Gazette"},
}

_mappings = {}
_metadata = {}

def _load_mappings():
    """Load mappings from JSON file, separating metadata from actual mappings."""
    global _mappings, _metadata
    try:
        if os.path.exists(_MAPPING_FILE):
            with open(_MAPPING_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Separate metadata from mappings
            _metadata = data.pop("_metadata", {})
            _mappings = data
        else:
            _mappings = _default_mappings.copy()
            _save_mappings()
    except Exception:
        _mappings = _default_mappings.copy()


def _save_mappings():
    """Save mappings to JSON file, preserving metadata."""
    try:
        # Combine metadata with mappings for saving
        data = {"_metadata": _metadata} if _metadata else {}
        data.update(_mappings)
        with open(_MAPPING_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

_load_mappings()

def map_ipc_to_bns(query: str) -> Optional[dict]:
    """
    Try exact match by number, then fuzzy match on keys.
    Returns mapping dict or None.
    """
    if not query:
        return None
    q = query.strip().lower().replace("ipc", "").replace("section", "").replace("s", "").strip()
    if q in _mappings:
        return _mappings[q]
    # try to extract numeric token
    tokens = [t for t in q.split() if any(ch.isdigit() for ch in t)]
    if tokens:
        for t in tokens:
            t = ''.join(ch for ch in t if ch.isdigit())
            if t in _mappings:
                return _mappings[t]
    # fuzzy match on keys
    close = get_close_matches(q, _mappings.keys(), n=1, cutoff=0.6)
    if close:
        return _mappings[close[0]]
    return None

# small helper to extend mapping at runtime (persists by default)
def add_mapping(ipc_section: str, bns_section: str, notes: str = "", source: str = "user", category: str = "User Added", persist: bool = True):
    """
    Add a new IPC to BNS mapping at runtime.
    
    Args:
        ipc_section: The IPC section number (e.g., "420")
        bns_section: The corresponding BNS section (e.g., "BNS 318")
        notes: Additional notes about the mapping
        source: Source of the mapping information
        category: Offense category for organization
        persist: Whether to save to disk immediately
    """
    key = str(ipc_section).strip()
    _mappings[key] = {
        "bns_section": bns_section, 
        "notes": notes, 
        "source": source,
        "category": category
    }
    if persist:
        _save_mappings()


def get_all_mappings() -> Dict[str, dict]:
    """
    Get all available IPC to BNS mappings.
    
    Returns:
        Dictionary of all mappings (excludes metadata).
    """
    return _mappings.copy()


def get_mappings_by_category(category: str) -> Dict[str, dict]:
    """
    Get all mappings belonging to a specific offense category.
    
    Args:
        category: The offense category to filter by (e.g., "Offenses Against Women")
    
    Returns:
        Dictionary of mappings in that category.
    """
    return {
        k: v for k, v in _mappings.items() 
        if v.get("category", "").lower() == category.lower()
    }


def get_categories() -> List[str]:
    """
    Get all available offense categories.
    
    Returns:
        List of unique category names.
    """
    categories = set()
    for mapping in _mappings.values():
        if isinstance(mapping, dict) and "category" in mapping:
            categories.add(mapping["category"])
    return sorted(list(categories))


def get_mapping_count() -> int:
    """
    Get the total number of IPC to BNS mappings available.
    
    Returns:
        Count of mappings (excludes metadata).
    """
    return len(_mappings)


def get_metadata() -> dict:
    """
    Get database metadata including version, sources, and update info.
    
    Returns:
        Metadata dictionary.
    """
    return _metadata.copy()
