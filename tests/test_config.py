import os

from engine.config import get_runtime_diagnostics, validate_runtime_config


def test_runtime_diagnostics_shape():
    data = get_runtime_diagnostics()
    assert isinstance(data, dict)
    for key in ("pdf_search", "ocr", "embeddings", "ollama"):
        assert key in data
        assert "status" in data[key]
        assert "reason" in data[key]


def test_validate_runtime_config_returns_list(monkeypatch):
    monkeypatch.setenv("LTA_USE_EMBEDDINGS", "1")
    warnings = validate_runtime_config()
    assert isinstance(warnings, list)
