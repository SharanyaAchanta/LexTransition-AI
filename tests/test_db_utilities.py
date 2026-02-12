import os
import sqlite3

from engine import db


def test_audit_trail_records_insert_and_update(tmp_path, monkeypatch):
    test_db = tmp_path / "audit.sqlite"
    monkeypatch.setattr(db, "_DB_FILE", str(test_db))
    db.initialize_db()

    assert db.upsert_mapping("111", "BNS 111", "note", "test", "cat", actor="test_case")
    assert db.upsert_mapping("111", "BNS 222", "note2", "test", "cat", actor="test_case")

    audit = db.get_mapping_audit("111", limit=10)
    assert len(audit) >= 2
    actions = [a["action"] for a in audit]
    assert "insert" in actions
    assert "update" in actions


def test_backup_and_restore(tmp_path, monkeypatch):
    test_db = tmp_path / "main.sqlite"
    backup_db = tmp_path / "backup.sqlite"
    monkeypatch.setattr(db, "_DB_FILE", str(test_db))
    db.initialize_db()
    assert db.upsert_mapping("420", "BNS 318", "x", "y", "z", actor="test_case")

    backup_path = db.backup_database(str(backup_db))
    assert backup_path is not None
    assert os.path.exists(backup_path)

    # Corrupt current DB then restore
    with open(test_db, "wb") as f:
        f.write(b"not a sqlite db")

    assert db.restore_database(str(backup_db)) is True
    conn = sqlite3.connect(str(test_db))
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM mappings")
    assert cur.fetchone()[0] >= 1
    conn.close()
