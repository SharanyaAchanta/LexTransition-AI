"""
Tiny RAG-like engine: PDF ingestion -> page-level search -> grounded citations.
Usage:
- index_pdfs() to auto-scan ./law_pdfs (create dir and add PDFs)
- add_pdf(file_path) to add a single PDF
- search_pdfs(query) -> formatted markdown string or None
"""
import os
import glob
import re
import json
import hashlib
import streamlit as st
import numpy as np

try:
    import pdfplumber
except Exception:
    pdfplumber = None

# Load the cached model
@st.cache_resource(show_spinner=False)
def load_embedding_model():
    """Loads the SentenceTransformer model into memory only once."""
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")

# Check environment config
_USE_EMB = os.environ.get("LTA_USE_EMBEDDINGS") == "1"
_EMB_AVAILABLE = False

# Validate dependencies availability
try:
    if _USE_EMB:
        from sentence_transformers import SentenceTransformer  # type: ignore
        _EMB_AVAILABLE = True

except Exception:
    _EMB_AVAILABLE = False
    _USE_EMB = False

# Try to import new embeddings engine (soft)
try:
    from engine.embeddings_engine import _EMB_AVAILABLE as _EMB_ENGINE_AVAILABLE, build_index as _build_emb_index, search as _emb_search_index
except Exception:
    _EMB_ENGINE_AVAILABLE = False

_INDEX = []        # page-level index
_INDEX_LOADED = False
_EMB_INDEX = []    # cached embeddings for current docs
_LAST_INDEX_STATS = {"processed_files": 0, "reused_files": 0, "deleted_files": 0, "total_docs": 0}

def _ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def _tokenize_query(query: str):
    # Keep alphanumeric chunks; drop punctuation-only fragments.
    return [t for t in re.findall(r"[A-Za-z0-9]+", query.lower()) if t]

def _cache_path(dir_path: str) -> str:
    return os.path.join(dir_path, ".rag_index_cache.json")

def _hash_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def _load_cache(dir_path: str):
    path = _cache_path(dir_path)
    if not os.path.exists(path):
        return {"files": {}}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and isinstance(data.get("files"), dict):
            return data
    except Exception:
        pass
    return {"files": {}}

def _save_cache(dir_path: str, cache: dict):
    path = _cache_path(dir_path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)

def get_index_diagnostics() -> dict:
    return dict(_LAST_INDEX_STATS)

def index_pdfs(dir_path="law_pdfs"):
    global _INDEX_LOADED, _INDEX, _EMB_INDEX, _LAST_INDEX_STATS
    _ensure_dir(dir_path)
    if pdfplumber is None:
        return False

    files = sorted(glob.glob(os.path.join(dir_path, "*.pdf")))
    cache = _load_cache(dir_path)
    cached_files = cache.get("files", {})
    new_cache = {"files": {}}
    processed_files = 0
    reused_files = 0

    if not files:
        _INDEX_LOADED = True
        _INDEX = []
        _EMB_INDEX = []
        _LAST_INDEX_STATS = {
            "processed_files": 0,
            "reused_files": 0,
            "deleted_files": len(cached_files),
            "total_docs": 0,
        }
        _save_cache(dir_path, new_cache)
        return True

    docs = []
    for f in files:
        abs_path = os.path.abspath(f)
        file_hash = ""
        try:
            file_hash = _hash_file(f)
        except Exception:
            processed_files += 1
            continue
        cached_entry = cached_files.get(abs_path)
        if cached_entry and cached_entry.get("hash") == file_hash and isinstance(cached_entry.get("docs"), list):
            reused_files += 1
            docs.extend(cached_entry["docs"])
            new_cache["files"][abs_path] = cached_entry
            continue
        processed_files += 1
        file_docs = []
        try:
            with pdfplumber.open(f) as pdf:
                for i, page in enumerate(pdf.pages, start=1):
                    text = (page.extract_text() or "").strip()
                    if text:
                        doc = {"file": os.path.basename(f), "page": i, "text": text}
                        file_docs.append(doc)
                        docs.append(doc)
        except Exception:
            continue
        new_cache["files"][abs_path] = {"hash": file_hash, "docs": file_docs}

    _INDEX = docs
    _INDEX_LOADED = True
    deleted_files = max(0, len(cached_files) - len(new_cache["files"]))
    _LAST_INDEX_STATS = {
        "processed_files": processed_files,
        "reused_files": reused_files,
        "deleted_files": deleted_files,
        "total_docs": len(_INDEX),
    }
    _save_cache(dir_path, new_cache)

    # Build Embeddings if enabled
    if _USE_EMB and _EMB_AVAILABLE:
        try:
            model = load_embedding_model()
            texts = [d["text"] for d in _INDEX]
            vecs = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
            _EMB_INDEX = []
            for d, v in zip(_INDEX, vecs):
                _EMB_INDEX.append({"file": d["file"], "page": d["page"], "text": d["text"], "vec": v})
        except Exception as e:
            print(f"Embedding generation failed: {e}")

    return True

def add_pdf(file_path):
    # call index_pdfs again after adding file to disk
    return index_pdfs(os.path.dirname(file_path) or "law_pdfs")

def clear_index():
    global _INDEX, _INDEX_LOADED, _EMB_INDEX, _LAST_INDEX_STATS
    _INDEX = []
    _INDEX_LOADED = True
    _EMB_INDEX = []
    _LAST_INDEX_STATS = {"processed_files": 0, "reused_files": 0, "deleted_files": 0, "total_docs": 0}

def _emb_search(query: str, top_k: int = 3):
    if not _EMB_INDEX or not _EMB_AVAILABLE:
        return None
    try:
        model = load_embedding_model()
        qvec = model.encode([query], convert_to_numpy=True)[0]

        scores = []
        for d in _EMB_INDEX:
            vec = d["vec"]
            sim = float(
                np.dot(qvec, vec) /
                (np.linalg.norm(qvec) * np.linalg.norm(vec) + 1e-9)
            )
            scores.append((sim, d["file"], d["page"], d["text"]))

        scores.sort(key=lambda x: x[0], reverse=True)

        structured_results = []
        for sim, file, page, text in scores[:top_k]:
            structured_results.append({
                "file": file,
                "page": page,
                "text": text,
                "score": sim
            })

        return structured_results

    except Exception:
        return None

def search_pdfs(query: str, top_k: int = 3):
    """
    Default: if an embeddings engine is configured -> use it.
    Else if internal embeddings available -> use that.
    Else -> keyword page-count search.
    """
    if not query or not query.strip():
        return None
    if top_k <= 0:
        return None

    # (Keep your existing external engine logic here)
    if os.environ.get("LTA_USE_EMBEDDINGS") == "1" and _EMB_ENGINE_AVAILABLE:
        try:
            emb_res = _emb_search_index(query, top_k=top_k)
            if emb_res:
                pass
    
        except Exception as e:
            print(f"External Embeddings Engine Failed: {e}")

    # (Keep your token-count fallback here)
    if not _INDEX_LOADED:
        index_pdfs()
    if not _INDEX:
        return None
    # -------- GET EMBEDDING RESULTS --------
    emb_results = []

    if _USE_EMB and _EMB_AVAILABLE:
        emb_res = _emb_search(query, top_k=top_k)
        if emb_res:
            emb_results = emb_res


    # -------- GET KEYWORD RESULTS --------
    tokens = _tokenize_query(query.strip())
    kw_results = []

    if tokens:
        scored = []
        for doc in _INDEX:
            txt = doc["text"].lower()
            score = sum(txt.count(t) for t in tokens)

            if score > 0:
                scored.append({
                    "file": doc["file"],
                    "page": doc["page"],
                    "text": doc["text"],
                    "score": float(score)
                })

        scored.sort(key=lambda x: x["score"], reverse=True)
        kw_results = scored[:top_k]

# -------- NORMALIZE EMBEDDING SCORES --------
    if emb_results:
        emb_scores = [item["score"] for item in emb_results]
        min_emb = min(emb_scores)
        max_emb = max(emb_scores)

        for item in emb_results:
            if max_emb > min_emb:
                item["score"] = (item["score"] - min_emb) / (max_emb - min_emb)
            else:
                item["score"] = 1.0


    # -------- NORMALIZE KEYWORD SCORES --------
    if kw_results:
        kw_scores = [item["score"] for item in kw_results]
        min_kw = min(kw_scores)
        max_kw = max(kw_scores)

        for item in kw_results:
            if max_kw > min_kw:
                item["score"] = (item["score"] - min_kw) / (max_kw - min_kw)
            else:
                item["score"] = 1.0
    # -------- HYBRID MERGE --------
    combined = {}

    for item in emb_results:
        key = (item["file"], item["page"])
        combined[key] = item

    for item in kw_results:
        key = (item["file"], item["page"])
        if key in combined:
            alpha = 0.6  # embedding weight
            beta = 0.4   # keyword weight
            combined[key]["score"] = alpha * combined[key]["score"] + beta * item["score"]
        else:
            combined[key] = item

    if not combined:
        return None

    final_results = sorted(
        combined.values(),
        key=lambda x: x["score"],
        reverse=True
    )

    return final_results[:top_k]
