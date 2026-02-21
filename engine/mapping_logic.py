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
from . import db

_base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_MAPPING_FILE = os.environ.get("LTA_MAPPING_DB") or os.path.join(_base_dir, "mapping_db.json")

# [UPDATED] Default mappings now include FULL TEXT for the demo
_default_mappings = {
    "420": {
        "bns_section": "BNS 318",
        "ipc_full_text": "Cheating and dishonestly inducing delivery of property.—Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person, or to make, alter or destroy the whole or any part of a valuable security, or anything which is signed or sealed, and which is capable of being converted into a valuable security, shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine.",
        "bns_full_text": "Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person, or to make, alter or destroy the whole or any part of a valuable security, or anything which is signed or sealed, and which is capable of being converted into a valuable security, shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine.",
        "notes": "Cheating and dishonestly inducing delivery of property",
        "category": "Cheating",
        "source": "Official Gazette"
    },
    "302": {
        "bns_section": "BNS 103",
        "ipc_full_text": "Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.",
        "bns_full_text": "Whoever commits murder shall be punished with death or imprisonment for life, and shall also be liable to fine. (2) When a group of five or more persons acting in concert commits murder on the ground of race, caste or community, sex, place of birth, language, personal belief or any other like ground each member of such group shall be punished with death or with imprisonment for life, and shall also be liable to fine.",
        "notes": "Punishment for murder",
        "category": "Offenses Against Human Body",
        "source": "Official Gazette"
    },
    "378": {
        "bns_section": "BNS 303",
        "ipc_full_text": "Theft.—Whoever, intending to take dishonestly any movable property out of the possession of any person without that person's consent, moves that property in order to such taking, is said to commit theft.",
        "bns_full_text": "Whoever, intending to take dishonestly any movable property out of the possession of any person without that person's consent, moves that property in order to such taking, is said to commit theft. (2) A theft is 'snatching' if, in order to commit theft, the offender suddenly or quickly or forcibly seizes or grabs or secures or grabs or takes away from any person or from his possession any movable property.",
        "notes": "Theft - Definition similar",
        "category": "Offenses Against Property",
        "source": "Official Gazette"
    },
}

_mappings = {}
_metadata = {}

def _load_mappings():
    """Load mappings from database."""
    global _mappings, _metadata
    try:
        # Load the SQLite db
        _mappings = db.get_all_mappings()
        _metadata = db.get_metadata()
        
        if not _mappings:
            # If DB is empty, use defaults and save to DB
            print("📦 DB is empty. Initializing with default mappings...")
            _mappings = _default_mappings.copy()
            for ipc_section, mapping in _mappings.items():
                db.insert_mapping(
                    ipc_section,
                    mapping["bns_section"],
                    mapping.get("ipc_full_text", ""), # full text
                    mapping.get("bns_full_text", ""), # Pass text
                    mapping["notes"],
                    mapping["source"],
                    mapping["category"]
                )
    except Exception as e:
        print(f"failed to load DB: {e}")
        _mappings = _default_mappings.copy()

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

# [UPDATED] Function signature to accept full text
def add_mapping(ipc_section: str, bns_section: str, 
                ipc_full_text: str = "", bns_full_text: str = "", 
                notes: str = "", source: str = "user", category: str = "User Added", persist: bool = True):
    """
    Add a new IPC to BNS mapping at runtime.
    """
    key = str(ipc_section).strip()

    # Backward compatibility for older positional calls:
    # add_mapping(ipc, bns, notes, source, persist=False)
    if notes == "" and source == "user" and category == "User Added":
        if bns_full_text:
            notes = ipc_full_text
            source = bns_full_text
            ipc_full_text = ""
            bns_full_text = ""
        elif ipc_full_text:
            notes = ipc_full_text
            ipc_full_text = ""
    
    # Update dictionary immediately
    mapping_data = {
        "bns_section": bns_section,
        "ipc_full_text": ipc_full_text,
        "bns_full_text": bns_full_text,
        "notes": notes,
        "source": source,
        "category": category
    }
    
    if persist:
        success = db.upsert_mapping(
            ipc_section=key,
            bns_section=bns_section,
            ipc_full_text=ipc_full_text,
            bns_full_text=bns_full_text,
            notes=notes,
            source=source,
            category=category,
            actor="ui",
        )
        if success:
            _mappings[key] = mapping_data
        return success
    else:
        _mappings[key] = mapping_data
        return True

def get_all_mappings() -> Dict[str, dict]:
    return _mappings.copy()

def get_mappings_by_category(category: str) -> Dict[str, dict]:
    return {
        k: v for k, v in _mappings.items() 
        if v.get("category", "").lower() == category.lower()
    }

def get_categories() -> List[str]:
    categories = set()
    for mapping in _mappings.values():
        if isinstance(mapping, dict) and "category" in mapping:
            categories.add(mapping["category"])
    return sorted(list(categories))

def get_mapping_count() -> int:
    return len(_mappings)

def get_metadata() -> dict:
    return _metadata.copy()
