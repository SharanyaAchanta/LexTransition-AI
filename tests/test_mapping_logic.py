import os
import json
import importlib
import tempfile
import sys

def test_mapping_persistence(tmp_path, monkeypatch):
    mapping_path = tmp_path / "test_mapping.json"
    # write initial mappings
    initial = {"111": {"bns_section": "BNS 111", "notes": "test", "source": "test"}}
    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(initial, f)
    monkeypatch.setenv("LTA_MAPPING_DB", str(mapping_path))

    # ensure fresh import uses our mapping file
    if "engine.mapping_logic" in sys.modules:
        del sys.modules["engine.mapping_logic"]
    ml = importlib.import_module("engine.mapping_logic")

    # exact lookup
    res = ml.map_ipc_to_bns("111")
    assert res is not None and res["bns_section"] == "BNS 111"

    # add a new mapping and confirm persistence
    ml.add_mapping("222", "BNS 222", "added by test")
    with open(mapping_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "222" in data and data["222"]["bns_section"] == "BNS 222"
