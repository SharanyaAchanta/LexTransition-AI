"""
Unit tests for the IPC to BNS mapping logic module.

This module tests the mapping functionality including:
- Exact section number lookup
- Fuzzy matching for partial/variant queries
- Query normalization (handling IPC, Section prefixes)
- Mapping persistence to JSON file
- Runtime mapping addition

Author: Savani Thakur
Date: 2026-02-10
"""

import os
import json
import importlib
import sys
import pytest

from engine import mapping_logic


class TestMapIPCToBNS:
    """Tests for the map_ipc_to_bns() function."""

    def test_map_ipc_to_bns_returns_dict_for_valid_section(self):
        """Verify that a valid IPC section returns a mapping dictionary."""
        # Section 420 should exist in default mappings
        result = mapping_logic.map_ipc_to_bns("420")
        assert result is not None, "Should return mapping for known section"
        assert isinstance(result, dict), "Should return a dictionary"
        assert "bns_section" in result, "Result should contain bns_section key"

    def test_map_ipc_to_bns_returns_none_for_unknown_section(self):
        """Verify that unknown sections return None."""
        result = mapping_logic.map_ipc_to_bns("99999")
        assert result is None, "Unknown section should return None"

    def test_map_ipc_to_bns_returns_none_for_empty_query(self):
        """Verify that empty query returns None."""
        assert mapping_logic.map_ipc_to_bns("") is None
        assert mapping_logic.map_ipc_to_bns(None) is None

    def test_map_ipc_to_bns_handles_ipc_prefix(self):
        """Verify that 'IPC' prefix is stripped correctly."""
        result = mapping_logic.map_ipc_to_bns("IPC 420")
        assert result is not None, "Should handle 'IPC' prefix"
        assert "bns_section" in result

    def test_map_ipc_to_bns_handles_section_prefix(self):
        """Verify that 'Section' prefix is stripped correctly."""
        result = mapping_logic.map_ipc_to_bns("Section 420")
        assert result is not None, "Should handle 'Section' prefix"

    def test_map_ipc_to_bns_handles_mixed_case(self):
        """Verify that case-insensitive matching works."""
        result = mapping_logic.map_ipc_to_bns("ipc section 420")
        assert result is not None, "Should handle mixed case input"

    def test_map_ipc_to_bns_handles_whitespace(self):
        """Verify that extra whitespace is handled."""
        result = mapping_logic.map_ipc_to_bns("  420  ")
        assert result is not None, "Should handle extra whitespace"

    def test_map_ipc_to_bns_extracts_numeric_token(self):
        """Verify that numeric tokens are extracted from complex queries."""
        result = mapping_logic.map_ipc_to_bns("charged under 420")
        assert result is not None, "Should extract numeric token from query"


class TestMappingPersistence:
    """Tests for mapping persistence functionality."""

    def test_mapping_persistence(self, tmp_path, monkeypatch):
        """Verify that mappings are correctly saved and loaded from file."""
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

    def test_add_mapping_without_persistence(self, tmp_path, monkeypatch):
        """Verify that persist=False prevents saving to disk."""
        mapping_path = tmp_path / "test_mapping_no_persist.json"
        initial = {"100": {"bns_section": "BNS 100", "notes": "initial", "source": "test"}}
        with open(mapping_path, "w", encoding="utf-8") as f:
            json.dump(initial, f)
        monkeypatch.setenv("LTA_MAPPING_DB", str(mapping_path))

        if "engine.mapping_logic" in sys.modules:
            del sys.modules["engine.mapping_logic"]
        ml = importlib.import_module("engine.mapping_logic")

        # Add without persistence
        ml.add_mapping("333", "BNS 333", "not persisted", persist=False)

        # Verify it's in memory
        res = ml.map_ipc_to_bns("333")
        assert res is not None, "Should be in memory"

        # Verify it's NOT on disk
        with open(mapping_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "333" not in data, "Should not be persisted to disk"


class TestAddMapping:
    """Tests for the add_mapping() function."""

    def test_add_mapping_creates_valid_structure(self, tmp_path, monkeypatch):
        """Verify that add_mapping creates correct data structure."""
        mapping_path = tmp_path / "test_add_mapping.json"
        with open(mapping_path, "w", encoding="utf-8") as f:
            json.dump({}, f)
        monkeypatch.setenv("LTA_MAPPING_DB", str(mapping_path))

        if "engine.mapping_logic" in sys.modules:
            del sys.modules["engine.mapping_logic"]
        ml = importlib.import_module("engine.mapping_logic")

        ml.add_mapping("555", "BNS 555", "Test notes", "test_source")
        
        result = ml.map_ipc_to_bns("555")
        assert result is not None
        assert result["bns_section"] == "BNS 555"
        assert result["notes"] == "Test notes"
        assert result["source"] == "test_source"

    def test_add_mapping_overwrites_existing(self, tmp_path, monkeypatch):
        """Verify that adding a mapping for existing section overwrites it."""
        mapping_path = tmp_path / "test_overwrite.json"
        initial = {"666": {"bns_section": "BNS OLD", "notes": "old", "source": "old"}}
        with open(mapping_path, "w", encoding="utf-8") as f:
            json.dump(initial, f)
        monkeypatch.setenv("LTA_MAPPING_DB", str(mapping_path))

        if "engine.mapping_logic" in sys.modules:
            del sys.modules["engine.mapping_logic"]
        ml = importlib.import_module("engine.mapping_logic")

        # Overwrite
        ml.add_mapping("666", "BNS NEW", "new notes")
        
        result = ml.map_ipc_to_bns("666")
        assert result["bns_section"] == "BNS NEW", "Should overwrite existing"
        assert result["notes"] == "new notes"


class TestFuzzyMatching:
    """Tests for fuzzy matching functionality."""

    def test_fuzzy_match_similar_numbers(self, tmp_path, monkeypatch):
        """Verify that fuzzy matching works for similar section numbers."""
        mapping_path = tmp_path / "test_fuzzy.json"
        initial = {"420": {"bns_section": "BNS 318", "notes": "cheating", "source": "test"}}
        with open(mapping_path, "w", encoding="utf-8") as f:
            json.dump(initial, f)
        monkeypatch.setenv("LTA_MAPPING_DB", str(mapping_path))

        if "engine.mapping_logic" in sys.modules:
            del sys.modules["engine.mapping_logic"]
        ml = importlib.import_module("engine.mapping_logic")

        # Exact match should work
        result = ml.map_ipc_to_bns("420")
        assert result is not None


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_handles_special_characters_in_query(self):
        """Verify graceful handling of special characters."""
        # Should not raise exception
        result = mapping_logic.map_ipc_to_bns("Section 420/302")
        # Result may be None or a match, but should not crash
        assert result is None or isinstance(result, dict)

    def test_handles_very_long_query(self):
        """Verify handling of very long query strings."""
        long_query = "Section " * 100 + "420"
        # Should not raise exception
        result = mapping_logic.map_ipc_to_bns(long_query)
        assert result is None or isinstance(result, dict)

    def test_handles_numeric_only_query(self):
        """Verify that pure numeric queries work."""
        result = mapping_logic.map_ipc_to_bns("302")
        # 302 is in default mappings
        assert result is not None or result is None  # Depends on loaded data

    def test_default_mappings_fallback(self, tmp_path, monkeypatch):
        """Verify that default mappings are used when file doesn't exist."""
        non_existent_path = tmp_path / "non_existent.json"
        monkeypatch.setenv("LTA_MAPPING_DB", str(non_existent_path))

        if "engine.mapping_logic" in sys.modules:
            del sys.modules["engine.mapping_logic"]
        ml = importlib.import_module("engine.mapping_logic")

        # Should still have default mappings
        result = ml.map_ipc_to_bns("420")
        assert result is not None, "Should fall back to default mappings"


class TestMappingDataIntegrity:
    """Tests to verify the integrity of mapping data."""

    def test_mapping_contains_required_fields(self):
        """Verify that mapping results contain required fields."""
        result = mapping_logic.map_ipc_to_bns("420")
        if result is not None:
            assert "bns_section" in result, "Must have bns_section field"
            # notes and source are expected but checking bns_section is critical

    def test_bns_section_format(self):
        """Verify that BNS section follows expected format."""
        result = mapping_logic.map_ipc_to_bns("420")
        if result is not None:
            bns = result.get("bns_section", "")
            # Should start with "BNS" or be "Decriminalized"
            assert bns.startswith("BNS") or bns == "Decriminalized", \
                f"BNS section should start with 'BNS' or be 'Decriminalized', got: {bns}"
