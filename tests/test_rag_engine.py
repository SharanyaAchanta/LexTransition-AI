import os
import tempfile
import importlib
from reportlab.pdfgen import canvas

def make_pdf(path, text):
    c = canvas.Canvas(str(path))
    c.setFont("Helvetica", 12)
    c.drawString(50, 800, text)
    c.showPage()
    c.save()

def test_pdf_index_and_search(tmp_path, monkeypatch):
    pdf_file = tmp_path / "sample_test.pdf"
    make_pdf(pdf_file, "This document is about theft and BNS section 303. It mentions the offence of theft.")

    # ensure fresh import to avoid prior index state
    if "engine.rag_engine" in globals():
        import sys
        if "engine.rag_engine" in sys.modules:
            del sys.modules["engine.rag_engine"]

    rag = importlib.import_module("engine.rag_engine")
    # index our temp dir
    assert rag.index_pdfs(str(tmp_path)) is True

    res = rag.search_pdfs("theft")
    assert res is not None
    assert "sample_test.pdf" in res
