import json
import os
import re

DATA_PATH = os.path.join("data", "bail_metadata.json")


def load_bail_data():
    """Load bail metadata from JSON file."""
    if not os.path.exists(DATA_PATH):
        return {}

    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def extract_sections(text: str):
    """
    Extract IPC/BNS sections from text.
    Example: 302, 420, 41A
    """
    if not text:
        return []

    matches = re.findall(r"\b\d+[A-Za-z]?\b", text)
    return list(set(matches))


def analyze_bail(text: str):
    """
    Main function to analyze bail eligibility.
    """
    metadata = load_bail_data()
    sections = extract_sections(text)

    results = []

    for sec in sections:
        info = metadata.get(sec)

        if info:
            results.append({
                    "section": sec,
                    "bailable": info.get("bailable", "Unknown"),
                    "cognizable": info.get("cognizable", "Unknown"),
                    "description": info.get("description", ""),
                    "procedure": info.get("procedure", ""),
                    "punishment": info.get("punishment", "Not specified")
                })

    return results