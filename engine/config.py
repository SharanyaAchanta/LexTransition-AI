"""
Runtime configuration diagnostics and validation helpers.
"""
from __future__ import annotations

import os
from typing import Dict, List


def _has_module(module_name: str) -> bool:
    try:
        __import__(module_name)
        return True
    except Exception:
        return False


def _ollama_health(url: str) -> bool:
    try:
        import requests
        resp = requests.get(f"{url.rstrip('/')}/api/tags", timeout=2)
        return bool(resp.ok)
    except Exception:
        return False


def get_runtime_diagnostics() -> Dict[str, Dict[str, str]]:
    """
    Returns per-feature diagnostics with status and reason.
    status values: ok, warn, error
    """
    use_emb = os.environ.get("LTA_USE_EMBEDDINGS") == "1"
    ollama_url = os.environ.get("LTA_OLLAMA_URL", "").strip()

    pdfplumber_ok = _has_module("pdfplumber")
    easyocr_ok = _has_module("easyocr")
    pytesseract_ok = _has_module("pytesseract")
    sentence_transformers_ok = _has_module("sentence_transformers")
    faiss_ok = _has_module("faiss")

    ocr_ok = easyocr_ok or pytesseract_ok
    embeddings_ok = (not use_emb) or (sentence_transformers_ok and faiss_ok)
    ollama_ok = (not ollama_url) or _ollama_health(ollama_url)

    return {
        "pdf_search": {
            "status": "ok" if pdfplumber_ok else "error",
            "reason": "pdfplumber available" if pdfplumber_ok else "pdfplumber missing",
        },
        "ocr": {
            "status": "ok" if ocr_ok else "warn",
            "reason": "easyocr/pytesseract available" if ocr_ok else "No OCR engine installed",
        },
        "embeddings": {
            "status": "ok" if embeddings_ok else "warn",
            "reason": (
                "Embeddings disabled by config"
                if not use_emb
                else "Dependencies missing for embeddings"
            ) if not embeddings_ok else ("Embeddings enabled and dependencies available" if use_emb else "Embeddings disabled by config"),
        },
        "ollama": {
            "status": "ok" if ollama_ok else "warn",
            "reason": (
                "Not configured"
                if not ollama_url
                else ("Configured and reachable" if ollama_ok else "Configured but not reachable")
            ),
        },
    }


def validate_runtime_config() -> List[str]:
    """
    Returns user-facing warnings for non-fatal misconfiguration.
    """
    diagnostics = get_runtime_diagnostics()
    warnings: List[str] = []
    for key, info in diagnostics.items():
        if info["status"] in {"warn", "error"}:
            warnings.append(f"{key}: {info['reason']}")
    return warnings
