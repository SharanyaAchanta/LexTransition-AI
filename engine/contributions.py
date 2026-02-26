"""
User Contributions Module for Legal Glossary

Provides functionality for users to contribute new legal terms
with a moderation queue for admin approval.

Features:
- Submit new term suggestions
- Moderation queue for approval/rejection
- View pending contributions
- Admin approval workflow
"""

import sqlite3
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Database file path (reuse glossary database)
_base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_GLOSSARY_DB_FILE = os.path.join(_base_dir, "glossary_db.sqlite")


def get_db_connection():
    """Get a database connection."""
    return sqlite3.connect(_GLOSSARY_DB_FILE)


def initialize_contributions_db():
    """Initialize the contributions table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create contributions/suggestions table
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
    """Submit a new term suggestion for moderation."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO term_contributions 
            (term, definition, related_sections, examples, category, submitter_name, submitter_email, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
        ''', (term, definition, related_sections, examples, category, submitter_name, submitter_email))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error submitting term suggestion: {e}")
        return False


def get_pending_contributions() -> List[Dict]:
    """Get all pending term contributions."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM term_contributions 
            WHERE status = 'pending'
            ORDER BY submitted_at DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'term': row[1],
                'definition': row[2],
                'related_sections': row[3],
                'examples': row[4],
                'category': row[5],
                'submitter_name': row[6],
                'submitter_email': row[7],
                'status': row[8],
                'submitted_at': row[9],
                'reviewed_at': row[10],
                'reviewed_by': row[11],
                'notes': row[12]
            }
            for row in rows
        ]
    except Exception as e:
        print(f"Error getting pending contributions: {e}")
        return []


def get_all_contributions(status: str = None) -> List[Dict]:
    """Get all contributions, optionally filtered by status."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
                SELECT * FROM term_contributions 
                WHERE status = ?
                ORDER BY submitted_at DESC
            ''', (status,))
        else:
            cursor.execute('''
                SELECT * FROM term_contributions 
                ORDER BY submitted_at DESC
            ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'term': row[1],
                'definition': row[2],
                'related_sections': row[3],
                'examples': row[4],
                'category': row[5],
                'submitter_name': row[6],
                'submitter_email': row[7],
                'status': row[8],
                'submitted_at': row[9],
                'reviewed_at': row[10],
                'reviewed_by': row[11],
                'notes': row[12]
            }
            for row in rows
        ]
    except Exception as e:
        print(f"Error getting all contributions: {e}")
        return []


def approve_contribution(contribution_id: int, reviewed_by: str = "Admin", notes: str = "") -> bool:
    """Approve a contribution and add it to the glossary."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get the contribution details
        cursor.execute("SELECT * FROM term_contributions WHERE id = ?", (contribution_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False
        
        term = row[1]
        definition = row[2]
        related_sections = row[3]
        examples = row[4]
        category = row[5]
        
        # Import glossary functions
        from engine.glossary import add_term
        
        # Try to add to glossary
        success = add_term(term, definition, related_sections, examples, category)
        
        if success:
            # Update contribution status
            cursor.execute('''
                UPDATE term_contributions 
                SET status = 'approved', reviewed_by = ?, reviewed_at = ?, notes = ?
                WHERE id = ?
            ''', (reviewed_by, datetime.now().isoformat(), notes, contribution_id))
            conn.commit()
        
        conn.close()
        return success
    except Exception as e:
        print(f"Error approving contribution: {e}")
        return False


def reject_contribution(contribution_id: int, reviewed_by: str = "Admin", 
                       notes: str = "Rejected") -> bool:
    """Reject a contribution."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE term_contributions 
            SET status = 'rejected', reviewed_by = ?, reviewed_at = ?, notes = ?
            WHERE id = ?
        ''', (reviewed_by, datetime.now().isoformat(), notes, contribution_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error rejecting contribution: {e}")
        return False


def get_contribution_count(status: str = "pending") -> int:
    """Get count of contributions by status."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM term_contributions WHERE status = ?
        ''', (status,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        print(f"Error getting contribution count: {e}")
        return 0


def delete_contribution(contribution_id: int) -> bool:
    """Delete a contribution record."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM term_contributions WHERE id = ?", (contribution_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    except Exception as e:
        print(f"Error deleting contribution: {e}")
        return False


# Initialize on import
initialize_contributions_db()
