import sqlite3
import os

DB_PATH = "mapping_db.sqlite"


def load_sections():
    """Load IPC and BNS sections from SQLite database."""
    if not os.path.exists(DB_PATH):
        return []

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT ipc_section, bns_section FROM mappings")

        rows = cursor.fetchall()
        conn.close()

        sections = set()

        for ipc, bns in rows:
            if ipc:
                sections.add(str(ipc))
            if bns:
                sections.add(str(bns))

        return sorted(list(sections))

    except Exception:
        return []


def get_suggestions(query: str, limit: int = 10):
    """Return matching suggestions."""
    sections = load_sections()

    if not query:
        return sections[:limit]

    query = query.lower()

    matches = [
        s for s in sections
        if query in s.lower()
    ]

    return matches[:limit]