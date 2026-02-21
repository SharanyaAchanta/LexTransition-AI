import os
import sqlite3

from engine import db


def test_backup_and_restore(tmp_path, monkeypatch):
    test_db = tmp_path / "main.sqlite"
    backup_db = tmp_path / "backup.sqlite"
    monkeypatch.setattr(db, "_DB_FILE", str(test_db))
    db.initialize_db()
    assert db.insert_mapping("420", "BNS 318", "x", "y", "z")

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
