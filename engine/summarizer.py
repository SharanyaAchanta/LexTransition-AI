import re


def extract_sections(text):
    return re.findall(r"\b\d+[A-Za-z]?\b", text)


def detect_authority(text):
    authorities = []

    if "police" in text.lower():
        authorities.append("Police")

    if "court" in text.lower():
        authorities.append("Court")

    return authorities


def generate_summary(text: str):
    if not text:
        return {}

    sections = extract_sections(text)
    authorities = detect_authority(text)

    action_points = []

    if "appear" in text.lower():
        action_points.append("You may need to appear before authorities.")

    if "notice" in text.lower():
        action_points.append("This document is an official notice.")

    summary = {
        "sections": list(set(sections)),
        "authorities": authorities,
        "action_points": action_points,
        "plain_summary": "This document contains legal instructions. Please review the sections mentioned and follow the guidance."
    }

    return summary