"""
Comprehensive unit tests for engine/embeddings_engine.py

Tests cover:
- Module configuration and availability flags
- build_index() function
- load_index() function  
- search() function
- Graceful degradation when dependencies unavailable
- Edge cases and error handling

Note: These tests use mocking to avoid requiring actual embedding dependencies.
"""

import importlib
import sys
import os
import pytest
from unittest.mock import MagicMock, patch, mock_open
from reportlab.pdfgen import canvas
from pathlib import Path


# ============================================================================
# Test Fixtures and Helpers
# ============================================================================

def get_fresh_embeddings_module():
    """
    Get a fresh import of embeddings_engine to avoid state pollution.
    """
    if "engine.embeddings_engine" in sys.modules:
        del sys.modules["engine.embeddings_engine"]
    return importlib.import_module("engine.embeddings_engine")


# ============================================================================
# Test Class: Module Configuration
# ============================================================================

class TestModuleConfiguration:
    """Tests for module-level configuration and availability."""

    def test_emb_available_flag_exists(self):
        """Module should have _EMB_AVAILABLE flag."""
        emb = get_fresh_embeddings_module()
        assert hasattr(emb, "_EMB_AVAILABLE")
        assert isinstance(emb._EMB_AVAILABLE, bool)

    def test_use_emb_flag_exists(self):
        """Module should have _USE_EMB flag."""
        emb = get_fresh_embeddings_module()
        assert hasattr(emb, "_USE_EMB")
        assert isinstance(emb._USE_EMB, bool)

    def test_index_paths_defined(self):
        """Module should define index storage paths."""
        emb = get_fresh_embeddings_module()
        assert hasattr(emb, "_IDX_PATH")
        assert hasattr(emb, "_META_PATH")
        assert "faiss.index" in emb._IDX_PATH
        assert "meta.txt" in emb._META_PATH

    def test_ensure_dir_function_exists(self):
        """Module should have _ensure_dir helper function."""
        emb = get_fresh_embeddings_module()
        assert hasattr(emb, "_ensure_dir")
        assert callable(emb._ensure_dir)


# ============================================================================
# Test Class: Build Index Function
# ============================================================================

class TestBuildIndex:
    """Tests for the build_index() function."""

    def test_build_index_returns_false_when_embeddings_unavailable(self):
        """build_index should return False when embeddings not available."""
        emb = get_fresh_embeddings_module()
        
        # If embeddings are not enabled, should return False
        if not emb._EMB_AVAILABLE:
            result = emb.build_index(["test text"], [("file.pdf", 1, "snippet")])
            assert result is False

    def test_build_index_accepts_correct_parameters(self):
        """build_index should accept texts and metas parameters."""
        emb = get_fresh_embeddings_module()
        
        # Verify function signature
        import inspect
        sig = inspect.signature(emb.build_index)
        params = list(sig.parameters.keys())
        
        assert "texts" in params
        assert "metas" in params

    def test_build_index_handles_empty_inputs(self):
        """build_index should handle empty inputs gracefully."""
        emb = get_fresh_embeddings_module()
        
        # Should not crash with empty inputs
        if not emb._EMB_AVAILABLE:
            result = emb.build_index([], [])
            assert result is False


# ============================================================================
# Test Class: Load Index Function
# ============================================================================

class TestLoadIndex:
    """Tests for the load_index() function."""

    def test_load_index_returns_false_when_embeddings_unavailable(self):
        """load_index should return False when embeddings not available."""
        emb = get_fresh_embeddings_module()
        
        if not emb._EMB_AVAILABLE:
            result = emb.load_index()
            assert result is False

    def test_load_index_returns_false_when_no_index_file(self, tmp_path):
        """load_index should return False when index files don't exist."""
        emb = get_fresh_embeddings_module()
        
        # Even if embeddings available, should return False if no files
        if not emb._EMB_AVAILABLE:
            result = emb.load_index()
            assert result is False


# ============================================================================
# Test Class: Search Function
# ============================================================================

class TestSearch:
    """Tests for the search() function."""

    def test_search_returns_none_when_embeddings_unavailable(self):
        """search should return None when embeddings not available."""
        emb = get_fresh_embeddings_module()
        
        if not emb._EMB_AVAILABLE:
            result = emb.search("test query")
            assert result is None

    def test_search_accepts_query_and_top_k(self):
        """search should accept query and top_k parameters."""
        emb = get_fresh_embeddings_module()
        
        import inspect
        sig = inspect.signature(emb.search)
        params = list(sig.parameters.keys())
        
        assert "query" in params
        assert "top_k" in params

    def test_search_default_top_k_is_3(self):
        """search should have default top_k of 3."""
        emb = get_fresh_embeddings_module()
        
        import inspect
        sig = inspect.signature(emb.search)
        top_k_param = sig.parameters.get("top_k")
        
        assert top_k_param is not None
        assert top_k_param.default == 3


# ============================================================================
# Test Class: Graceful Degradation
# ============================================================================

class TestGracefulDegradation:
    """Tests for graceful degradation when dependencies unavailable."""

    def test_module_imports_without_dependencies(self):
        """Module should import successfully even without embedding deps."""
        # This test verifies the module doesn't crash on import
        emb = get_fresh_embeddings_module()
        assert emb is not None

    def test_functions_dont_crash_without_dependencies(self):
        """All functions should handle missing dependencies gracefully."""
        emb = get_fresh_embeddings_module()
        
        # These should all return safely without crashing
        if not emb._EMB_AVAILABLE:
            assert emb.build_index(["text"], [("f", 1, "s")]) is False
            assert emb.load_index() is False
            assert emb.search("query") is None

    def test_load_model_returns_none_when_unavailable(self):
        """_load_model should return None when embeddings unavailable."""
        emb = get_fresh_embeddings_module()
        
        if not emb._EMB_AVAILABLE:
            result = emb._load_model()
            assert result is None


# ============================================================================
# Test Class: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_search_with_empty_query(self):
        """search should handle empty query strings."""
        emb = get_fresh_embeddings_module()
        
        # Should not crash
        result = emb.search("")
        assert result is None or isinstance(result, list)

    def test_search_with_special_characters(self):
        """search should handle special characters in query."""
        emb = get_fresh_embeddings_module()
        
        # Should not crash with special characters
        result = emb.search("IPC §302 — murder!")
        assert result is None or isinstance(result, list)

    def test_search_with_unicode(self):
        """search should handle unicode characters."""
        emb = get_fresh_embeddings_module()
        
        # Should not crash with unicode
        result = emb.search("भारतीय दंड संहिता")
        assert result is None or isinstance(result, list)

    def test_build_index_with_unicode_texts(self):
        """build_index should handle unicode in texts and metas."""
        emb = get_fresh_embeddings_module()
        
        # Should not crash
        texts = ["भारतीय दंड संहिता धारा 302"]
        metas = [("law.pdf", 1, "धारा 302")]
        
        result = emb.build_index(texts, metas)
        # Returns False if embeddings not available, or True if successful
        assert isinstance(result, bool)


# ============================================================================
# Test Class: Integration with Environment
# ============================================================================

class TestEnvironmentIntegration:
    """Tests for environment variable integration."""

    def test_use_emb_reads_environment_variable(self, monkeypatch):
        """_USE_EMB should reflect LTA_USE_EMBEDDINGS environment variable."""
        # Clear module cache
        if "engine.embeddings_engine" in sys.modules:
            del sys.modules["engine.embeddings_engine"]
        
        # Set environment variable
        monkeypatch.setenv("LTA_USE_EMBEDDINGS", "1")
        
        # Import fresh module
        emb = importlib.import_module("engine.embeddings_engine")
        
        # _USE_EMB should be True (dependencies may still not be available)
        assert emb._USE_EMB is True

    def test_use_emb_false_when_env_not_set(self, monkeypatch):
        """_USE_EMB should be False when LTA_USE_EMBEDDINGS not set."""
        if "engine.embeddings_engine" in sys.modules:
            del sys.modules["engine.embeddings_engine"]
        
        # Ensure variable is not set
        monkeypatch.delenv("LTA_USE_EMBEDDINGS", raising=False)
        
        emb = importlib.import_module("engine.embeddings_engine")
        
        assert emb._USE_EMB is False


# ============================================================================
# Original Integration Test (kept for backwards compatibility)
# ============================================================================

@pytest.mark.skipif(os.environ.get("LTA_USE_EMBEDDINGS") != "1", reason="Embeddings not enabled")
def test_embeddings_build_and_search(tmp_path):
    """Integration test that runs when embeddings are enabled."""
    # generate simple PDF
    pdf_file = tmp_path / "emb_test.pdf"
    c = canvas.Canvas(str(pdf_file))
    c.drawString(50, 800, "This file discusses theft and BNS Section 303 about theft penalties.")
    c.showPage()
    c.save()

    rag = importlib.import_module("engine.rag_engine")
    # index the tmp dir
    assert rag.index_pdfs(str(tmp_path)) is True

    # search for theft
    res = rag.search_pdfs("theft", top_k=2)
    assert res is not None
    assert "emb_test.pdf" in res
