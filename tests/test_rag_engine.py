"""
Comprehensive unit tests for engine/rag_engine.py

Tests cover:
- PDF indexing (index_pdfs)
- PDF search (search_pdfs)
- Index management (clear_index, add_pdf)
- Edge cases and error handling
"""

import os
import sys
import importlib
import pytest
from reportlab.pdfgen import canvas


# ============================================================================
# Test Fixtures and Helpers
# ============================================================================

def make_pdf(path, text):
    """Create a simple PDF with given text."""
    c = canvas.Canvas(str(path))
    c.setFont("Helvetica", 12)
    c.drawString(50, 800, text)
    c.showPage()
    c.save()


def make_multipage_pdf(path, pages_text):
    """Create a multi-page PDF with given text per page."""
    c = canvas.Canvas(str(path))
    for text in pages_text:
        c.setFont("Helvetica", 12)
        c.drawString(50, 800, text)
        c.showPage()
    c.save()


def get_fresh_rag_module():
    """
    Get a fresh import of rag_engine to avoid state pollution between tests.
    """
    if "engine.rag_engine" in sys.modules:
        del sys.modules["engine.rag_engine"]
    return importlib.import_module("engine.rag_engine")


# ============================================================================
# Test Class: PDF Indexing
# ============================================================================

class TestIndexPdfs:
    """Tests for the index_pdfs() function."""

    def test_index_pdfs_returns_true_on_success(self, tmp_path):
        """index_pdfs should return True when successful."""
        pdf_file = tmp_path / "test.pdf"
        make_pdf(pdf_file, "Sample legal document about IPC Section 302.")
        
        rag = get_fresh_rag_module()
        result = rag.index_pdfs(str(tmp_path))
        
        assert result is True

    def test_index_pdfs_empty_directory(self, tmp_path):
        """index_pdfs should handle empty directories gracefully."""
        rag = get_fresh_rag_module()
        result = rag.index_pdfs(str(tmp_path))
        
        assert result is True

    def test_index_pdfs_creates_directory_if_missing(self, tmp_path):
        """index_pdfs should create the directory if it doesn't exist."""
        nonexistent_dir = tmp_path / "new_pdf_dir"
        
        rag = get_fresh_rag_module()
        result = rag.index_pdfs(str(nonexistent_dir))
        
        assert result is True
        assert nonexistent_dir.exists()

    def test_index_pdfs_processes_multiple_files(self, tmp_path):
        """index_pdfs should process multiple PDF files."""
        make_pdf(tmp_path / "doc1.pdf", "Document about theft under IPC 379.")
        make_pdf(tmp_path / "doc2.pdf", "Document about murder under IPC 302.")
        make_pdf(tmp_path / "doc3.pdf", "Document about fraud under IPC 420.")
        
        rag = get_fresh_rag_module()
        result = rag.index_pdfs(str(tmp_path))
        
        assert result is True

    def test_index_pdfs_handles_multipage_pdf(self, tmp_path):
        """index_pdfs should index all pages of a multi-page PDF."""
        pdf_file = tmp_path / "multipage.pdf"
        make_multipage_pdf(pdf_file, [
            "Page 1: IPC Section 302 deals with murder.",
            "Page 2: IPC Section 376 deals with assault.",
            "Page 3: IPC Section 420 deals with cheating."
        ])
        
        rag = get_fresh_rag_module()
        result = rag.index_pdfs(str(tmp_path))
        
        assert result is True

    def test_index_pdfs_ignores_non_pdf_files(self, tmp_path):
        """index_pdfs should only process .pdf files."""
        # Create a PDF and some non-PDF files
        make_pdf(tmp_path / "legal.pdf", "Legal document content.")
        (tmp_path / "notes.txt").write_text("Some notes.")
        (tmp_path / "data.json").write_text("{}")
        
        rag = get_fresh_rag_module()
        result = rag.index_pdfs(str(tmp_path))
        
        assert result is True


# ============================================================================
# Test Class: PDF Search
# ============================================================================

class TestSearchPdfs:
    """Tests for the search_pdfs() function."""

    def test_search_pdfs_finds_matching_content(self, tmp_path):
        """search_pdfs should find documents containing query terms."""
        pdf_file = tmp_path / "sample_test.pdf"
        make_pdf(pdf_file, "This document is about theft and BNS section 303.")
        
        rag = get_fresh_rag_module()
        rag.index_pdfs(str(tmp_path))
        
        result = rag.search_pdfs("theft")
        
        assert result is not None
        assert "sample_test.pdf" in result

    def test_search_pdfs_returns_none_for_empty_query(self, tmp_path):
        """search_pdfs should return None for empty or whitespace queries."""
        make_pdf(tmp_path / "doc.pdf", "Some content here.")
        
        rag = get_fresh_rag_module()
        rag.index_pdfs(str(tmp_path))
        
        assert rag.search_pdfs("") is None
        assert rag.search_pdfs("   ") is None
        assert rag.search_pdfs(None) is None

    def test_search_pdfs_returns_none_for_no_matches(self, tmp_path):
        """search_pdfs should return None when no documents match."""
        make_pdf(tmp_path / "doc.pdf", "This is about criminal law.")
        
        rag = get_fresh_rag_module()
        rag.index_pdfs(str(tmp_path))
        
        result = rag.search_pdfs("xyz123nonexistent")
        
        assert result is None

    def test_search_pdfs_case_insensitive(self, tmp_path):
        """search_pdfs should be case-insensitive."""
        make_pdf(tmp_path / "doc.pdf", "This document discusses MURDER under IPC.")
        
        rag = get_fresh_rag_module()
        rag.index_pdfs(str(tmp_path))
        
        result = rag.search_pdfs("murder")
        
        assert result is not None
        assert "doc.pdf" in result

    def test_search_pdfs_multiple_terms(self, tmp_path):
        """search_pdfs should handle multiple search terms."""
        make_pdf(tmp_path / "doc.pdf", "IPC Section 302 covers murder and homicide.")
        
        rag = get_fresh_rag_module()
        rag.index_pdfs(str(tmp_path))
        
        result = rag.search_pdfs("murder homicide")
        
        assert result is not None

    def test_search_pdfs_returns_markdown_format(self, tmp_path):
        """search_pdfs should return results in markdown format."""
        make_pdf(tmp_path / "legal.pdf", "Section 420 of IPC covers cheating.")
        
        rag = get_fresh_rag_module()
        rag.index_pdfs(str(tmp_path))
        
        result = rag.search_pdfs("cheating")
        
        assert result is not None
        assert "**Source:**" in result
        assert "**Page:**" in result

    def test_search_pdfs_respects_top_k(self, tmp_path):
        """search_pdfs should respect the top_k parameter."""
        # Create multiple PDFs with the same keyword
        for i in range(5):
            make_pdf(tmp_path / f"doc{i}.pdf", f"Document {i} about theft and crime.")
        
        rag = get_fresh_rag_module()
        rag.index_pdfs(str(tmp_path))
        
        result = rag.search_pdfs("theft", top_k=2)
        
        assert result is not None
        # Count occurrences of "Source:" to verify top_k limit
        source_count = result.count("**Source:**")
        assert source_count <= 2


# ============================================================================
# Test Class: Index Management
# ============================================================================

class TestIndexManagement:
    """Tests for clear_index() and add_pdf() functions."""

    def test_clear_index_resets_state(self, tmp_path):
        """clear_index should reset the index to empty state."""
        make_pdf(tmp_path / "doc.pdf", "Some searchable content here.")
        
        rag = get_fresh_rag_module()
        rag.index_pdfs(str(tmp_path))
        
        # Verify content is indexed
        assert rag.search_pdfs("searchable") is not None
        
        # Clear and verify
        rag.clear_index()
        assert rag.search_pdfs("searchable") is None

    def test_add_pdf_reindexes_directory(self, tmp_path):
        """add_pdf should trigger re-indexing of the directory."""
        pdf_file = tmp_path / "new_doc.pdf"
        make_pdf(pdf_file, "New document about extortion.")
        
        rag = get_fresh_rag_module()
        result = rag.add_pdf(str(pdf_file))
        
        assert result is True


# ============================================================================
# Test Class: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_handles_special_characters_in_query(self, tmp_path):
        """search_pdfs should handle special characters in query."""
        make_pdf(tmp_path / "doc.pdf", "Section 302-A of the IPC.")
        
        rag = get_fresh_rag_module()
        rag.index_pdfs(str(tmp_path))
        
        # Should not crash with special characters
        result = rag.search_pdfs("302-A")
        # May or may not find results, but shouldn't crash
        assert result is None or isinstance(result, str)

    def test_handles_unicode_in_query(self, tmp_path):
        """search_pdfs should handle unicode characters."""
        make_pdf(tmp_path / "doc.pdf", "Legal document content.")
        
        rag = get_fresh_rag_module()
        rag.index_pdfs(str(tmp_path))
        
        # Should not crash with unicode
        result = rag.search_pdfs("भारतीय दंड संहिता")
        assert result is None or isinstance(result, str)

    def test_handles_very_long_query(self, tmp_path):
        """search_pdfs should handle very long queries."""
        make_pdf(tmp_path / "doc.pdf", "Brief content.")
        
        rag = get_fresh_rag_module()
        rag.index_pdfs(str(tmp_path))
        
        long_query = "legal " * 1000
        result = rag.search_pdfs(long_query)
        assert result is None or isinstance(result, str)

    def test_search_without_prior_indexing(self, tmp_path):
        """search_pdfs should handle being called without prior indexing."""
        rag = get_fresh_rag_module()
        
        # Should not crash, may return None
        result = rag.search_pdfs("anything")
        assert result is None or isinstance(result, str)

    def test_index_pdfs_handles_corrupted_pdf(self, tmp_path):
        """index_pdfs should gracefully handle corrupted PDF files."""
        # Create a fake "PDF" with invalid content
        corrupted = tmp_path / "corrupted.pdf"
        corrupted.write_bytes(b"This is not a valid PDF file")
        
        # Also create a valid PDF
        make_pdf(tmp_path / "valid.pdf", "Valid content here.")
        
        rag = get_fresh_rag_module()
        # Should not crash, should still index the valid PDF
        result = rag.index_pdfs(str(tmp_path))
        
        assert result is True


# ============================================================================
# Test Class: Integration Tests
# ============================================================================

class TestRAGIntegration:
    """Integration tests for the RAG workflow."""

    def test_full_workflow_index_search_clear(self, tmp_path):
        """Test complete workflow: index -> search -> clear -> search again."""
        make_pdf(tmp_path / "law.pdf", "IPC Section 302 prescribes punishment for murder.")
        
        rag = get_fresh_rag_module()
        
        # Index
        assert rag.index_pdfs(str(tmp_path)) is True
        
        # Search should find results
        result = rag.search_pdfs("murder")
        assert result is not None
        assert "law.pdf" in result
        
        # Clear index
        rag.clear_index()
        
        # Search should return None after clearing
        result = rag.search_pdfs("murder")
        assert result is None

    def test_reindexing_picks_up_new_files(self, tmp_path):
        """Reindexing should pick up newly added PDF files."""
        make_pdf(tmp_path / "original.pdf", "Original document content.")
        
        rag = get_fresh_rag_module()
        rag.index_pdfs(str(tmp_path))
        
        # Add new PDF
        make_pdf(tmp_path / "newfile.pdf", "New document about cybercrime.")
        
        # Reindex
        rag.index_pdfs(str(tmp_path))
        
        # Should find new content
        result = rag.search_pdfs("cybercrime")
        assert result is not None
        assert "newfile.pdf" in result
