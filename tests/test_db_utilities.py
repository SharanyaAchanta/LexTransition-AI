from engine import db


def test_audit_trail_records_insert_and_update(tmp_path, monkeypatch):
    test_db = tmp_path / "audit.sqlite"
    monkeypatch.setattr(db, "_DB_FILE", str(test_db))
    db.initialize_db()

    assert db.upsert_mapping(
        ipc_section="111",
        bns_section="BNS 111",
        notes="note",
        source="test",
        category="cat",
        actor="test_case",
    )
    assert db.upsert_mapping(
        ipc_section="111",
        bns_section="BNS 222",
        notes="note2",
        source="test",
        category="cat",
        actor="test_case",
    )

    audit = db.get_mapping_audit("111", limit=10)
    assert len(audit) >= 2
    actions = [a["action"] for a in audit]
    assert "insert" in actions
    assert "update" in actions
