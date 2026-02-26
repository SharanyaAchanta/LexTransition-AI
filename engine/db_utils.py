"""
Database utilities for the IPC to BNS mapping system.

Provides reusable database helpers, row mappers, and context managers
to reduce code duplication in db.py.
"""

import sqlite3
import json
import os
from contextlib import contextmanager
from typing import Dict, List, Optional, Any, Tuple
from typing import Callable


def _get_db_file():
    """Get the database file path. Imports from db to avoid circular import at module load time."""
    from engine.db import _DB_FILE as db_file
    return db_file


@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    
    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # ... do stuff
        # Connection automatically closed
    
    Yields:
        sqlite3.Connection: Database connection
    """
    conn = None
    try:
        conn = sqlite3.connect(_get_db_file())
        yield conn
    finally:
        if conn is not None:
            conn.close()


class DatabaseHelper:
    """
    Helper class for common database operations.
    
    Provides methods for executing queries with consistent error handling
    and connection management.
    """
    
    @staticmethod
    def fetch_one(query: str, params: Tuple = ()) -> Optional[List]:
        """
        Execute a query and fetch a single row.
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            
        Returns:
            List of column values or None if no row found
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchone()
        except Exception as e:
            print(f"Error executing fetch_one: {e}")
            return None
    
    @staticmethod
    def fetch_all(query: str, params: Tuple = ()) -> List[List]:
        """
        Execute a query and fetch all rows.
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            
        Returns:
            List of rows, each row is a list of column values
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error executing fetch_all: {e}")
            return []
    
    @staticmethod
    def execute(query: str, params: Tuple = (), commit: bool = True) -> bool:
        """
        Execute a query that modifies data (INSERT, UPDATE, DELETE).
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            commit: Whether to commit the transaction
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                if commit:
                    conn.commit()
                return True
        except Exception as e:
            print(f"Error executing: {e}")
            return False
    
    @staticmethod
    def execute_with_cursor(cursor: sqlite3.Cursor, query: str, params: Tuple = ()) -> bool:
        """
        Execute a query using an existing cursor (for transactions).
        
        Args:
            cursor: Existing database cursor
            query: SQL query string
            params: Query parameters tuple
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor.execute(query, params)
            return True
        except Exception as e:
            print(f"Error executing with cursor: {e}")
            return False


# Row Mapper Functions

def map_row_to_mapping(row: Optional[List], include_ipc_key: bool = False, ipc_key: str = "") -> Optional[Dict]:
    """
    Map a database row to a mapping dictionary.
    
    Expected row structure:
        (ipc_section, bns_section, ipc_full_text, bns_full_text, notes, source, category)
    
    Args:
        row: Database row as list of values
        include_ipc_key: If True, use ipc_key as dictionary key
        ipc_key: The IPC section to use as key when include_ipc_key is True
        
    Returns:
        Dictionary representation of the mapping or None
    """
    if row is None:
        return None
    
    mapping = {
        'bns_section': row[1],
        'ipc_full_text': row[2],
        'bns_full_text': row[3],
        'notes': row[4],
        'source': row[5],
        'category': row[6]
    }
    
    if include_ipc_key:
        return {ipc_key: mapping}
    return mapping


def map_row_to_full_mapping(row: Optional[List]) -> Optional[Dict]:
    """
    Map a database row to a full mapping dictionary including ipc_section.
    
    Expected row structure:
        (ipc_section, bns_section, ipc_full_text, bns_full_text, notes, source, category)
    
    Args:
        row: Database row as list of values
        
    Returns:
        Full dictionary representation of the mapping or None
    """
    if row is None:
        return None
    
    return {
        'ipc_section': row[0],
        'bns_section': row[1],
        'ipc_full_text': row[2],
        'bns_full_text': row[3],
        'notes': row[4],
        'source': row[5],
        'category': row[6]
    }


def map_row_to_audit_entry(row: Optional[List]) -> Optional[Dict]:
    """
    Map a database row to an audit entry dictionary.
    
    Expected row structure:
        (id, action, ipc_section, previous_value, new_value, actor, created_at)
    
    Args:
        row: Database row as list of values
        
    Returns:
        Dictionary representation of the audit entry or None
    """
    if row is None:
        return None
    
    return {
        "id": row[0],
        "action": row[1],
        "ipc_section": row[2],
        "previous_value": json.loads(row[3] or "{}"),
        "new_value": json.loads(row[4] or "{}"),
        "actor": row[5],
        "created_at": row[6],
    }


def map_rows_to_mappings(rows: List[List], include_ipc_key: bool = False) -> Dict[str, Dict]:
    """
    Map multiple database rows to a mappings dictionary.
    
    Args:
        rows: List of database rows
        include_ipc_key: If True, use ipc_section as dictionary key
        
    Returns:
        Dictionary of mappings
    """
    mappings = {}
    for row in rows:
        if include_ipc_key:
            mappings[row[0]] = map_row_to_mapping(row)
        else:
            # For get_all_mappings, ipc_section is the key
            mappings[row[0]] = {
                'bns_section': row[1],
                'ipc_full_text': row[2],
                'bns_full_text': row[3],
                'notes': row[4],
                'source': row[5],
                'category': row[6]
            }
    return mappings
