"""
Persistent database module for IPC to BNS mapping system using SQLite.

Provides database operations including initialization, CRUD operations,
import/export functionality, and migration from JSON.
"""

import sqlite3
import json
import os
import shutil
import logging
logger = logging.getLogger(__name__)
import pandas as pd
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from pathlib import Path

_base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_DB_FILE = os.path.join(_base_dir, "mapping_db.sqlite")
_JSON_FILE = os.path.join(_base_dir, "mapping_db.json")

def get_db_connection():
    """Get a database connection."""
    return sqlite3.connect(_DB_FILE)

def initialize_db():
    """Initialize the database and create tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create mappings table with full text
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mappings (
            ipc_section TEXT PRIMARY KEY,
            bns_section TEXT NOT NULL,
            ipc_full_text TEXT,
            bns_full_text TEXT,
            notes TEXT,
            source TEXT,
            category TEXT
        )
    ''')

    # Create metadata table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    # Create audit trail table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mapping_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            ipc_section TEXT NOT NULL,
            previous_value TEXT,
            new_value TEXT,
            actor TEXT,
            created_at TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _serialize_mapping(mapping: Optional[Dict]) -> str:
    return json.dumps(mapping or {}, ensure_ascii=False)

def _log_audit(
    cursor: sqlite3.Cursor,
    action: str,
    ipc_section: str,
    previous_value: Optional[Dict],
    new_value: Optional[Dict],
    actor: str = "system",
) -> None:
    cursor.execute(
        """
        INSERT INTO mapping_audit (action, ipc_section, previous_value, new_value, actor, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            action,
            ipc_section,
            _serialize_mapping(previous_value),
            _serialize_mapping(new_value),
            actor,
            _utc_now_iso(),
        ),
    )

def migrate_from_json():
    """Migrate existing JSON data to database on first run."""
    if not os.path.exists(_JSON_FILE):
        return

    if os.path.exists(_DB_FILE):
        # Already migrated
        return

    initialize_db()

    try:
        with open(_JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert metadata
        metadata = data.pop('_metadata', {})
        for key, value in metadata.items():
            cursor.execute(
                "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
                (key, json.dumps(value))
            )

        # Insert mappings
        for ipc_section, mapping in data.items():
            cursor.execute('''
                INSERT INTO mappings (ipc_section, bns_section, ipc_full_text, bns_full_text, notes, source, category)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                ipc_section,
                mapping.get('bns_section', ''),
                mapping.get('ipc_full_text', ''),
                mapping.get('bns_full_text', ''),
                mapping.get('notes', ''),
                mapping.get('source', ''),
                mapping.get('category', '')
            ))

        conn.commit()
        conn.close()
        logger.info(f"Successfully migrated {len(data)} mappings from JSON to database.")

    except Exception as e:
        logger.error(f"Error during migration: {e}")

def insert_mapping(ipc_section: str, bns_section: str, 
                   ipc_full_text: str = "", bns_full_text: str = "", 
                   notes: str = "", source: str = "user", category: str = "User Added",
                   actor: str = "system") -> bool:
    """Insert a single mapping into the database."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO mappings (ipc_section, bns_section, ipc_full_text, bns_full_text, notes, source, category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (ipc_section, bns_section, ipc_full_text, bns_full_text, notes, source, category))
        new_value = {
            "ipc_section": ipc_section,
            "bns_section": bns_section,
            "ipc_full_text": ipc_full_text,
            "bns_full_text": bns_full_text,
            "notes": notes,
            "source": source,
            "category": category,
        }
        _log_audit(cursor, "insert", ipc_section, None, new_value, actor=actor)

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        logger.warning(f"⚠️ DB Warning: Section {ipc_section} already exists.")
        return False
    except Exception as e:
        logger.error(f"Error inserting mapping: {e}")
        return False
    finally:
        if conn is not None:
            conn.close()

def get_mapping(ipc_section: str) -> Optional[Dict]:
    """Get a single mapping by IPC section."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM mappings WHERE ipc_section = ?", (ipc_section,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'ipc_section': row[0],
                'bns_section': row[1],
                'ipc_full_text': row[2],
                'bns_full_text': row[3],
                'notes': row[4],
                'source': row[5],
                'category': row[6]
            }
        return None

    except Exception as e:
        logger.error(f"Error getting mapping: {e}")
        return None

def get_all_mappings() -> Dict[str, Dict]:
    """Get all mappings as a dictionary."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM mappings")
        rows = cursor.fetchall()
        conn.close()

        mappings = {}
        for row in rows:
            mappings[row[0]] = {
                'bns_section': row[1],
                'ipc_full_text': row[2],
                'bns_full_text': row[3],
                'notes': row[4],
                'source': row[5],
                'category': row[6]
            }
        return mappings

    except Exception as e:
        logger.error(f"Error getting all mappings: {e}")
        return {}

def get_mappings_by_category(category: str) -> Dict[str, Dict]:
    """Get mappings by category."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM mappings WHERE category = ?", (category,))
        rows = cursor.fetchall()
        conn.close()

        mappings = {}
        for row in rows:
            mappings[row[0]] = {
                'bns_section': row[1],
                'ipc_full_text': row[2],
                'bns_full_text': row[3],
                'notes': row[4],
                'source': row[5],
                'category': row[6]
            }
        return mappings

    except Exception as e:
        logger.error(f"Error getting mappings by category: {e}")
        return {}

def get_categories() -> List[str]:
    """Get all unique categories."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT DISTINCT category FROM mappings")
        rows = cursor.fetchall()
        conn.close()

        return [row[0] for row in rows if row[0]]

    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return []

def get_mapping_count() -> int:
    """Get total number of mappings."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM mappings")
        count = cursor.fetchone()[0]
        conn.close()

        return count

    except Exception as e:
        logger.error(f"Error getting mapping count: {e}")
        return 0

def get_metadata() -> Dict:
    """Get metadata from database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT key, value FROM metadata")
        rows = cursor.fetchall()
        conn.close()

        metadata = {}
        for key, value in rows:
            try:
                metadata[key] = json.loads(value)
            except:
                metadata[key] = value
        return metadata

    except Exception as e:
        logger.error(f"Error getting metadata: {e}")
        return {}

def update_mapping(
    ipc_section: str,
    bns_section: str,
    ipc_full_text: str = "",
    bns_full_text: str = "",
    notes: str = "",
    source: str = "user",
    category: str = "User Added",
    actor: str = "system",
) -> bool:
    """Update an existing mapping. Returns False if mapping doesn't exist."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mappings WHERE ipc_section = ?", (ipc_section,))
        row = cursor.fetchone()
        if not row:
            return False
        previous = {
            "ipc_section": row[0],
            "bns_section": row[1],
            "ipc_full_text": row[2],
            "bns_full_text": row[3],
            "notes": row[4],
            "source": row[5],
            "category": row[6],
        }
        cursor.execute(
            """
            UPDATE mappings
            SET bns_section = ?, ipc_full_text = ?, bns_full_text = ?, notes = ?, source = ?, category = ?
            WHERE ipc_section = ?
            """,
            (bns_section, ipc_full_text, bns_full_text, notes, source, category, ipc_section),
        )
        new_value = {
            "ipc_section": ipc_section,
            "bns_section": bns_section,
            "ipc_full_text": ipc_full_text,
            "bns_full_text": bns_full_text,
            "notes": notes,
            "source": source,
            "category": category,
        }
        _log_audit(cursor, "update", ipc_section, previous, new_value, actor=actor)
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Error updating mapping: {e}")
        return False
    finally:
        if conn is not None:
            conn.close()

def upsert_mapping(
    ipc_section: str,
    bns_section: str,
    ipc_full_text: str = "",
    bns_full_text: str = "",
    notes: str = "",
    source: str = "user",
    category: str = "User Added",
    actor: str = "system",
) -> bool:
    """Insert or update mapping and write audit trail."""
    existing = get_mapping(ipc_section)
    if existing is None:
        return insert_mapping(
            ipc_section=ipc_section,
            bns_section=bns_section,
            ipc_full_text=ipc_full_text,
            bns_full_text=bns_full_text,
            notes=notes,
            source=source,
            category=category,
            actor=actor,
        )
    return update_mapping(
        ipc_section=ipc_section,
        bns_section=bns_section,
        ipc_full_text=ipc_full_text,
        bns_full_text=bns_full_text,
        notes=notes,
        source=source,
        category=category,
        actor=actor,
    )

def get_mapping_audit(ipc_section: Optional[str] = None, limit: int = 100) -> List[Dict]:
    """Get audit trail entries, newest first."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if ipc_section:
            cursor.execute(
                """
                SELECT id, action, ipc_section, previous_value, new_value, actor, created_at
                FROM mapping_audit
                WHERE ipc_section = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (ipc_section, limit),
            )
        else:
            cursor.execute(
                """
                SELECT id, action, ipc_section, previous_value, new_value, actor, created_at
                FROM mapping_audit
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            )
        rows = cursor.fetchall()
        conn.close()
        entries = []
        for row in rows:
            entries.append(
                {
                    "id": row[0],
                    "action": row[1],
                    "ipc_section": row[2],
                    "previous_value": json.loads(row[3] or "{}"),
                    "new_value": json.loads(row[4] or "{}"),
                    "actor": row[5],
                    "created_at": row[6],
                }
            )
        return entries
    except Exception as e:
        logger.error(f"Error getting mapping audit: {e}")
        return []

def backup_database(backup_path: Optional[str] = None) -> Optional[str]:
    """Create a timestamped SQLite backup and return path."""
    try:
        if not os.path.exists(_DB_FILE):
            return None
        backup_dir = os.path.join(os.path.dirname(_DB_FILE), "backups")
        os.makedirs(backup_dir, exist_ok=True)
        if backup_path is None:
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            backup_path = os.path.join(backup_dir, f"mapping_db_{stamp}.sqlite")
        shutil.copy2(_DB_FILE, backup_path)
        return backup_path
    except Exception as e:
        logger.error(f"Error backing up database: {e}")
        return None

def _check_sqlite_integrity(db_path: str) -> bool:
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        result = cursor.fetchone()
        return bool(result and str(result[0]).lower() == "ok")
    except Exception:
        return False
    finally:
        if conn is not None:
            conn.close()

def restore_database(backup_path: str) -> bool:
    """Restore database from backup file after integrity validation."""
    try:
        if not os.path.exists(backup_path):
            return False
        if not _check_sqlite_integrity(backup_path):
            return False
        if os.path.exists(_DB_FILE):
            pre_restore = backup_database()
            if pre_restore is None:
                return False
        shutil.copy2(backup_path, _DB_FILE)
        return _check_sqlite_integrity(_DB_FILE)
    except Exception as e:
        logger.error(f"Error restoring database: {e}")
        return False


def import_mappings_from_csv(file_path: str) -> Tuple[int, List[str]]:
    """Import mappings from CSV file."""
    errors = []
    success_count = 0

    try:
        df = pd.read_csv(file_path)

        # Validate required columns
        required_cols = ['ipc_section', 'bns_section']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {', '.join(missing_cols)}")
            return 0, errors

        for _, row in df.iterrows():
            try:
                ipc_section = str(row['ipc_section']).strip()
                bns_section = str(row['bns_section']).strip()
                # Safe .get() calls for optional text columns
                ipc_full_text = str(row.get('ipc_full_text', '')).strip()
                bns_full_text = str(row.get('bns_full_text', '')).strip()
                notes = str(row.get('notes', '')).strip()
                source = str(row.get('source', 'imported')).strip()
                category = str(row.get('category', 'Imported')).strip()

                if upsert_mapping(
                    ipc_section=ipc_section,
                    bns_section=bns_section,
                    ipc_full_text=ipc_full_text,
                    bns_full_text=bns_full_text,
                    notes=notes,
                    source=source,
                    category=category,
                    actor="import_csv",
                ):
                    success_count += 1

            except Exception as e:
                errors.append(f"Error importing row {len(errors) + success_count + 1}: {e}")

    except Exception as e:
        errors.append(f"Error reading CSV file: {e}")

    return success_count, errors


def import_mappings_from_excel(file_path: str) -> Tuple[int, List[str]]:
    """Import mappings from Excel file."""
    errors = []
    success_count = 0

    try:
        df = pd.read_excel(file_path)

        # Validate required columns
        required_cols = ['ipc_section', 'bns_section']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {', '.join(missing_cols)}")
            return 0, errors

        for _, row in df.iterrows():
            try:
                ipc_section = str(row['ipc_section']).strip()
                bns_section = str(row['bns_section']).strip()
                # Safe .get() calls for optional text columns
                ipc_full_text = str(row.get('ipc_full_text', '')).strip()
                bns_full_text = str(row.get('bns_full_text', '')).strip()
                notes = str(row.get('notes', '')).strip()
                source = str(row.get('source', 'imported')).strip()
                category = str(row.get('category', 'Imported')).strip()

                if upsert_mapping(
                    ipc_section=ipc_section,
                    bns_section=bns_section,
                    ipc_full_text=ipc_full_text,
                    bns_full_text=bns_full_text,
                    notes=notes,
                    source=source,
                    category=category,
                    actor="import_excel",
                ):
                    success_count += 1

            except Exception as e:
                errors.append(f"Error importing row {len(errors) + success_count + 1}: {e}")

    except Exception as e:
        errors.append(f"Error reading Excel file: {e}")

    return success_count, errors


def export_mappings_to_json(file_path: str) -> bool:
    """Export all mappings to JSON file."""
    try:
        mappings = get_all_mappings()
        metadata = get_metadata()

        data = {"_metadata": metadata}
        data.update(mappings)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return True

    except Exception as e:
        logger.error(f"Error exporting to JSON: {e}")
        return False


def export_mappings_to_csv(file_path: str) -> bool:
    """Export all mappings to CSV file."""
    try:
        mappings = get_all_mappings()

        data = []
        for ipc_section, mapping in mappings.items():
            data.append({
                'ipc_section': ipc_section,
                'bns_section': mapping['bns_section'],
                'ipc_full_text': mapping.get('ipc_full_text', ''),
                'bns_full_text': mapping.get('bns_full_text', ''),
                'notes': mapping['notes'],
                'source': mapping['source'],
                'category': mapping['category']
            })

        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)

        return True

    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
        return False

# Initialize database on import
initialize_db()
migrate_from_json()
