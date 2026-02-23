import json
import os
import uuid

BOOKMARK_FILE = "bookmarks.json"


def load_bookmarks():
    if not os.path.exists(BOOKMARK_FILE):
        return []

    with open(BOOKMARK_FILE, "r") as f:
        return json.load(f)


def save_bookmarks(bookmarks):
    with open(BOOKMARK_FILE, "w") as f:
        json.dump(bookmarks, f, indent=4)


def add_bookmark(section, title, notes):
    bookmarks = load_bookmarks()

    new_entry = {
        "id": str(uuid.uuid4()),
        "section": section,
        "title": title,
        "notes": notes
    }

    bookmarks.append(new_entry)
    save_bookmarks(bookmarks)

    print("✅ Bookmark saved successfully!")


def view_bookmarks():
    bookmarks = load_bookmarks()

    if not bookmarks:
        print("No bookmarks found.")
        return

    for b in bookmarks:
        print("\n--------------------")
        print(f"ID: {b['id']}")
        print(f"Section: {b['section']}")
        print(f"Title: {b['title']}")
        print(f"Notes: {b['notes']}")


def delete_bookmark(bookmark_id):
    bookmarks = load_bookmarks()
    updated = [b for b in bookmarks if b["id"] != bookmark_id]

    save_bookmarks(updated)
    print("🗑️ Bookmark deleted.")


def edit_bookmark(bookmark_id, new_notes):
    bookmarks = load_bookmarks()

    for b in bookmarks:
        if b["id"] == bookmark_id:
            b["notes"] = new_notes

    save_bookmarks(bookmarks)
    print("✏️ Bookmark updated.")