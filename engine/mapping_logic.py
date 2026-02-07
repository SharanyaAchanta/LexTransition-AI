"""
IPC -> BNS mapping helper (small seed dataset).
Provides exact lookup and fuzzy matching for section numbers/queries.
"""
import os
import json
from difflib import get_close_matches
from typing import Optional

_base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_MAPPING_FILE = os.environ.get("LTA_MAPPING_DB") or os.path.join(_base_dir, "mapping_db.json")

_default_mappings = {
    "420": {"bns_section": "BNS 318", "notes": "Cheating mapping; penalties similar but reorganized", "source": "mapping_db.json"},
    "302": {"bns_section": "BNS 501", "notes": "Homicide mapping stub", "source": "mapping_db.json"},
    "378": {"bns_section": "BNS 410", "notes": "Theft mapping stub", "source": "mapping_db.json"},
}

_mappings = {}

def _load_mappings():
    global _mappings
    try:
        if os.path.exists(_MAPPING_FILE):
            with open(_MAPPING_FILE, "r", encoding="utf-8") as f:
                _mappings = json.load(f)
        else:
            _mappings = _default_mappings.copy()
            _save_mappings()
    except Exception:
        _mappings = _default_mappings.copy()

def _save_mappings():
    try:
        with open(_MAPPING_FILE, "w", encoding="utf-8") as f:
            json.dump(_mappings, f, indent=2, ensure_ascii=False)
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
def add_mapping(ipc_section: str, bns_section: str, notes: str = "", source: str = "user", persist: bool = True):
    key = str(ipc_section).strip()
    _mappings[key] = {"bns_section": bns_section, "notes": notes, "source": source}
    if persist:
        _save_mappings()
