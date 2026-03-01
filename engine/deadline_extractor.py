import re
from datetime import datetime


def extract_dates(text: str):
    """
    Extract possible dates from legal text.
    Supports formats like:
    12/05/2024
    12-05-2024
    12 May 2024
    """

    if not text:
        return []

    patterns = [
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        r"\b\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s\d{2,4}\b",
    ]

    matches = []

    for pattern in patterns:
        matches.extend(re.findall(pattern, text, re.IGNORECASE))

    return list(set(matches))


def analyze_deadlines(text: str):
    """
    Analyze extracted dates and classify urgency.
    """

    dates = extract_dates(text)

    results = []

    today = datetime.today()

    for d in dates:
        try:
            parsed = datetime.strptime(d, "%d/%m/%Y")
        except:
            try:
                parsed = datetime.strptime(d, "%d-%m-%Y")
            except:
                parsed = None

        status = "Unknown"

        if parsed:
            diff = (parsed - today).days

            if diff < 0:
                status = "Expired"
            elif diff <= 3:
                status = "Urgent"
            else:
                status = "Upcoming"

        results.append({
            "date": d,
            "status": status
        })

    return results