import requests
import streamlit as st
from datetime import datetime, timedelta
import sqlite3
import os
from typing import Dict, List, Optional, Tuple

# --- GitHub Stats ---
@st.cache_data(ttl=3600)
def get_github_stats(repo_full_name="SharanyaAchanta/LexTransition-AI"):
    """
    Fetches GitHub repository statistics with caching to respect rate limits.
    """
    cache_key = f"github_stats_{repo_full_name}"
    if cache_key in st.session_state:
        stats, timestamp = st.session_state[cache_key]
        if datetime.now() - timestamp < timedelta(minutes=10):
            return stats
    stats = {
        "stars": 0,
        "forks": 0,
        "issues": 0,
        "pull_requests": 0,
        "last_updated": None
    }
    try:
        repo_url = f"https://api.github.com/repos/{repo_full_name}"
        repo_response = requests.get(repo_url, timeout=5)
        if repo_response.status_code == 200:
            repo_data = repo_response.json()
            stats["stars"] = repo_data.get("stargazers_count", 0)
            stats["forks"] = repo_data.get("forks_count", 0)
            stats["issues"] = repo_data.get("open_issues_count", 0)
        pulls_url = f"https://api.github.com/repos/{repo_full_name}/pulls?state=open"
        pulls_response = requests.get(pulls_url, timeout=5)
        if pulls_response.status_code == 200:
            stats["pull_requests"] = len(pulls_response.json())
            stats["issues"] = max(0, stats["issues"] - stats["pull_requests"])
        stats["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state[cache_key] = (stats, datetime.now())
        return stats
    except Exception as e:
        print(f"Error fetching GitHub stats: {e}")
        return stats

# --- Contributions (Glossary Terms) ---
_base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_GLOSSARY_DB_FILE = os.path.join(_base_dir, "glossary_db.sqlite")

def get_db_connection():
    return sqlite3.connect(_GLOSSARY_DB_FILE)

def initialize_contributions_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS term_contributions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term TEXT NOT NULL,
            definition TEXT NOT NULL,
            related_sections TEXT,
            examples TEXT,
            category TEXT,
            submitter_name TEXT,
            submitter_email TEXT,
            status TEXT DEFAULT 'pending',
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TIMESTAMP,
            reviewed_by TEXT,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

def submit_term_suggestion(term: str, definition: str, related_sections: str = "",
                          examples: str = "", category: str = "General",
                          submitter_name: str = "Anonymous",
                          submitter_email: str = "") -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO term_contributions (term, definition, related_sections, examples, category, submitter_name, submitter_email)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (term, definition, related_sections, examples, category, submitter_name, submitter_email))
    conn.commit()
    conn.close()
    return True

def get_pending_contributions() -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM term_contributions WHERE status = 'pending' ORDER BY submitted_at DESC''')
    rows = cursor.fetchall()
    conn.close()
    keys = [desc[0] for desc in cursor.description]
    return [dict(zip(keys, row)) for row in rows]

def approve_contribution(contribution_id: int, reviewer: str = "Admin") -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''UPDATE term_contributions SET status = 'approved', reviewed_at = CURRENT_TIMESTAMP, reviewed_by = ? WHERE id = ?''', (reviewer, contribution_id))
    conn.commit()
    conn.close()
    return True

def reject_contribution(contribution_id: int, reviewer: str = "Admin", notes: str = "") -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''UPDATE term_contributions SET status = 'rejected', reviewed_at = CURRENT_TIMESTAMP, reviewed_by = ?, notes = ? WHERE id = ?''', (reviewer, notes, contribution_id))
    conn.commit()
    conn.close()
    return True
