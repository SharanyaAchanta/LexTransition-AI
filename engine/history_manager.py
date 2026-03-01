import json
import os
from datetime import datetime

HISTORY_FILE = "search_history.json"

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []

    with open(HISTORY_FILE, "r") as f:
        return json.load(f)

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)


def add_history(query, result):
    history = load_history()

    entry = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "result": result,
    }

    history.append(entry)
    save_history(history)


def view_history():
    history = load_history()

    if not history:
        print("No search history found.")
        return

    for h in history:
        print("\n----------------------")
        print(f"Time: {h['timestamp']}")
        print(f"Query: {h['query']}")
        print(f"Result: {h['result']}")


def clear_history():
    save_history([])
    print("Search history cleared.")