import importlib
import pytest
import os
from reportlab.pdfgen import canvas
from pathlib import Path

@pytest.mark.skipif(os.environ.get("LTA_USE_EMBEDDINGS") != "1", reason="Embeddings not enabled")
def test_embeddings_build_and_search(tmp_path):
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
