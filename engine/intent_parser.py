import re
# from engine.bookmark_manager import add_bookmark  # Uncomment when ready to link!

# --- The Brain: Keyword Dictionaries ---
INTENT_MAP = {
    "analyze": ["analyze", "analysis", "break down", "explain"],
    "summarize": ["summarize", "summary", "short", "brief"],
    "raw_text": ["raw text", "exact text", "full text", "read"],
    "bookmark_add": ["bookmark", "save", "pin", "add to bookmarks"],
    "export_pdf": ["export pdf", "download pdf", "save as pdf", "export result", "download"]
}

def parse_intent(text: str) -> dict:
    """Parses natural language into actionable variables."""
    text_lower = text.lower()
    result = {"target": None, "action": None, "payload": None}

    # 1. Extract Target (e.g., "302", "498A")
    target_match = re.search(r'\b(\d{1,3}[A-Za-z]?)\b', text_lower)
    if target_match:
        result["target"] = target_match.group(1).upper()

    # 2. Extract Action
    for action, keywords in INTENT_MAP.items():
        if any(kw in text_lower for kw in keywords):
            result["action"] = action
            break # Stop at the first matched intent

    # 3. Extract Payload (Notes) - specifically useful for bookmarks
    note_match = re.search(r'(?:with the note|note|saying)[\s:]+(.*)', text_lower)
    if note_match:
        result["payload"] = note_match.group(1).strip()

    return result

def execute_intent(parsed_data: dict, text_query: str):
    """Routes the parsed data to the actual backend or UI triggers."""
    action = parsed_data.get("action")
    target = parsed_data.get("target")
    payload = parsed_data.get("payload")

    print(f"\n Heard: '{text_query}'")
    print(f"Action: {action} | Target: {target} | Payload: {payload}")

    # --- Backend Executions ---
    if action == "bookmark_add":
        if not target:
            return "Error: Could not find a section number to bookmark."
        try:
            # add_bookmark(section=target, notes=payload or "")
            return f"Successfully bookmarked Section {target} with note: '{payload}'"
        except Exception as e:
            return f"Failed to bookmark: {e}"

    # --- UI State Triggers ---
    elif action in ["analyze", "summarize", "raw_text"]:
        return f"🔜 [UI TRIGGER]: Auto-opening the '{action}' view for Section {target}."
    
    elif action == "copy_mapping":
        return f"🔜 [UI TRIGGER]: Mapping results for Section {target} copied to clipboard!"
        
    elif action == "export_pdf":
        return f"🔜 [UI TRIGGER]: Exporting Mapping results for Section {target} to PDF."
    
    else:
        return "🤷‍♂️ No actionable intent recognized. Proceeding with standard search."
    
    for query in test_queries:
        parsed = parse_intent(query)
        print(execute_intent(parsed, query))