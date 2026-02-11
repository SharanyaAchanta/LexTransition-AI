"""
Tiny RAG-like engine: PDF ingestion -> page-level search -> grounded citations.
Usage:
- index_pdfs() to auto-scan ./law_pdfs (create dir and add PDFs)
- add_pdf(file_path) to add a single PDF
- search_pdfs(query) -> formatted markdown string or None
"""
import os
import glob
import streamlit as st
import numpy as np
from collections import Counter

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

def _ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def index_pdfs(dir_path="law_pdfs"):
    global _INDEX_LOADED, _INDEX, _EMB_INDEX
    _ensure_dir(dir_path)
    if pdfplumber is None:
        return False
        
    # Standard file reading 
    files = glob.glob(os.path.join(dir_path, "*.pdf"))
    if not files:
        _INDEX_LOADED = True
        _INDEX = []
        _EMB_INDEX = []
        return True
        
    docs = []
    for f in files:
        try:
            with pdfplumber.open(f) as pdf:
                for i, page in enumerate(pdf.pages, start=1):
                    text = (page.extract_text() or "").strip()
                    if text:
                        docs.append({"file": os.path.basename(f), "page": i, "text": text})
        except Exception:
            continue
    _INDEX = docs
    _INDEX_LOADED = True

    # Build Embeddings if enabled
    if _USE_EMB and _EMB_AVAILABLE:
        try:
            # --- USE CACHED MODEL HERE ---
            model = load_embedding_model()
            
            texts = [d["text"] for d in _INDEX]
            # Generate embeddings using the cached model
            vecs = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
            
            _EMB_INDEX = []
            for d, v in zip(_INDEX, vecs):
                _EMB_INDEX.append({"file": d["file"], "page": d["page"], "text": d["text"], "vec": v})
        except Exception as e:
            print(f"Embedding generation failed: {e}")
            pass

    return True

def add_pdf(file_path):
    # call index_pdfs again after adding file to disk
    return index_pdfs(os.path.dirname(file_path) or "law_pdfs")

def clear_index():
    global _INDEX, _INDEX_LOADED, _EMB_INDEX
    _INDEX = []
    _INDEX_LOADED = True
    _EMB_INDEX = []

def _emb_search(query: str, top_k: int = 3):
    if not _EMB_INDEX or not _EMB_AVAILABLE:
        return None
    try:
        # --- USE CACHED MODEL HERE ---
        model = load_embedding_model()
        
        qvec = model.encode([query], convert_to_numpy=True)[0]
        scores = []
        for d in _EMB_INDEX:
            vec = d["vec"]
            # cosine similarity
            sim = float(np.dot(qvec, vec) / (np.linalg.norm(qvec) * np.linalg.norm(vec) + 1e-9))
            scores.append((sim, d["file"], d["page"], d["text"]))
        scores.sort(key=lambda x: x[0], reverse=True)
        
        results = scores[:top_k]
        md = ["> **Answer (embedding search, grounded):**\n"]
        for sim, file, page, text in results:
            snippet = text[:300].replace("\n", " ")
            md.append(f"> - **Source:** {file} | **Page:** {page} | **Score:** {sim:.3f}\n>   > _{snippet}_\n")
        return "\n".join(md)
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

    # (Keep your existing external engine logic here)
    if os.environ.get("LTA_USE_EMBEDDINGS") == "1" and _EMB_ENGINE_AVAILABLE:
        try:
            emb_res = _emb_search_index(query, top_k=top_k)
            if emb_res:
                return emb_res

    # Internal embeddings fallback
    if _USE_EMB and _EMB_AVAILABLE:
        emb_res = _emb_search(query, top_k=top_k)
        if emb_res:
            return emb_res

    # (Keep your token-count fallback here)
    if not _INDEX_LOADED:
        index_pdfs()
    if not _INDEX:
        return None
    q = query.lower().strip()
    tokens = [t for t in q.split() if t]
    if not tokens:
        return None
    scored = []
    for doc in _INDEX:
        txt = doc["text"].lower()
        score = sum(txt.count(t) for t in tokens)
        if score > 0:
            first_pos = min((txt.find(t) for t in tokens if txt.find(t) >= 0), default=-1)
            snippet = doc["text"][first_pos:first_pos+300].replace("\n"," ") if first_pos >= 0 else doc["text"][:200]
            scored.append((score, doc["file"], doc["page"], snippet))
    if not scored:
        return None
    scored.sort(key=lambda x: x[0], reverse=True)
    results = scored[:top_k]
    md_lines = ["> **Answer (grounded snippets):**\n"]
    for score, file, page, snippet in results:
        md_lines.append(f"> - **Source:** {file} | **Page:** {page}\n>   > _{snippet.strip()}_\n")
    return "\n".join(md_lines)
