import re
punishments = {
    "302": "Murder — life imprisonment or death penalty.",
    "420": "Cheating — imprisonment up to 7 years and fine.",
    "41A": "Notice of appearance before police officer."
}


def extract_sections(text: str):
    """
    Detect IPC/BNS sections only when keywords like
    Section / Sec / U/S are present.
    Avoid capturing dates.
    """
    import re

    if not text:
        return []

    pattern = r"(?:section|sec|u/s)\s*(\d{1,3}[A-Za-z]?)"

    matches = re.findall(pattern, text, re.IGNORECASE)

    return list(set(matches))

def calculate_severity(sections):
    """
    Improved severity classification based on section numbers.
    """

    highest = 0

    for sec in sections:
        try:
            num = int(re.findall(r"\d+", sec)[0])
            highest = max(highest, num)
        except:
            continue

    if highest >= 300:
        return "High"
    elif highest >= 150:
        return "Medium"
    elif highest > 0:
        return "Low"
    else:
        return "Low"

def generate_guidance(level):
    """
    Provide legal guidance text.
    """
    if level == "High":
        return "Serious offense detected. Immediate legal consultation is strongly recommended."
    elif level == "Medium":
        return "Moderate legal risk identified. Consider consulting a legal professional."
    else:
        return "Low severity indicators detected. Monitor the situation carefully."


def analyze_risk(text: str):
    """
    Main pipeline function.
    """
    sections = extract_sections(text)
    severity = calculate_severity(sections)
    guidance = generate_guidance(severity)

    return {
        "sections": sections,
        "severity": severity,
        "guidance": guidance
    }