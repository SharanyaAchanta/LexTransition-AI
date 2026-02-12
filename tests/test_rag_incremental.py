import importlib
import sys

from reportlab.pdfgen import canvas


def _make_pdf(path, text):
    c = canvas.Canvas(str(path))
    c.setFont("Helvetica", 12)
    c.drawString(50, 800, text)
    c.showPage()
    c.save()


def _fresh_rag():
    if "engine.rag_engine" in sys.modules:
        del sys.modules["engine.rag_engine"]
    return importlib.import_module("engine.rag_engine")


def test_incremental_index_reuses_unchanged_files(tmp_path):
    rag = _fresh_rag()
    pdf = tmp_path / "law.pdf"
    _make_pdf(pdf, "IPC Section 302 and murder details")

    assert rag.index_pdfs(str(tmp_path)) is True
    first = rag.get_index_diagnostics()
    assert first["processed_files"] >= 1

    # Re-index without changes should reuse cached content.
    assert rag.index_pdfs(str(tmp_path)) is True
    second = rag.get_index_diagnostics()
    assert second["reused_files"] >= 1


def test_search_output_contains_offsets(tmp_path):
    rag = _fresh_rag()
    pdf = tmp_path / "law.pdf"
    _make_pdf(pdf, "Cheating is covered under IPC 420 and related provisions.")
    rag.index_pdfs(str(tmp_path))

    res = rag.search_pdfs("cheating")
    assert res is not None
    assert "**Offsets:**" in res
