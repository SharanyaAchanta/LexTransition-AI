"""
Embeddings engine (optional).
- Uses sentence-transformers to encode texts.
- Uses faiss (faiss-cpu) + numpy for a simple persistent index stored under ./vector_store.
Environment:
- Set LTA_USE_EMBEDDINGS=1 to enable.
"""
import os
from typing import List, Optional, Tuple

_USE_EMB = os.environ.get("LTA_USE_EMBEDDINGS") == "1"

# graceful-degrade imports
_EMB_AVAILABLE = False
try:
    if _USE_EMB:
        from sentence_transformers import SentenceTransformer  # type: ignore
        import numpy as np  # type: ignore
        import faiss  # type: ignore
        _EMB_AVAILABLE = True
except Exception:
    _EMB_AVAILABLE = False

_IDX_DIR = os.path.join(os.path.dirname(__file__), "..", "vector_store")
_IDX_PATH = os.path.join(_IDX_DIR, "faiss.index")
_META_PATH = os.path.join(_IDX_DIR, "meta.txt")
_MODEL = None
_INDEX = None
_META: List[Tuple[str, int, str]] = []

def _ensure_dir():
    os.makedirs(_IDX_DIR, exist_ok=True)

def _load_model():
    global _MODEL
    if not _EMB_AVAILABLE:
        return None
    if _MODEL is None:
        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _MODEL

def build_index(texts: List[str], metas: List[Tuple[str, int, str]]):
    """
    texts: list of strings to index
    metas: list of metadata tuples (file, page, snippet)
    Returns True on success, False otherwise.
    """
    if not _EMB_AVAILABLE:
        return False
    _ensure_dir()
    model = _load_model()
    vecs = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    dim = vecs.shape[1]
    # Normalize for inner-product similarity
    faiss.normalize_L2(vecs)
    index = faiss.IndexFlatIP(dim)
    index.add(vecs)
    faiss.write_index(index, _IDX_PATH)
    with open(_META_PATH, "w", encoding="utf-8") as f:
        for m in metas:
            f.write(f"{m[0]}\t{m[1]}\t{m[2].replace(chr(10),' ').replace(chr(13),' ')}\n")
    return True

def load_index():
    global _INDEX, _META
    if not _EMB_AVAILABLE:
        return False
    if not os.path.exists(_IDX_PATH) or not os.path.exists(_META_PATH):
        return False
    _INDEX = faiss.read_index(_IDX_PATH)
    _META = []
    with open(_META_PATH, "r", encoding="utf-8") as f:
        for ln in f:
            parts = ln.rstrip("\n").split("\t")
            if len(parts) >= 3:
                _META.append((parts[0], int(parts[1]), parts[2]))
    return True

def search(query: str, top_k: int = 3) -> Optional[List[Tuple[float, str, int, str]]]:
    """
    Returns list of (score, file, page, snippet) or None.
    """
    if not _EMB_AVAILABLE:
        return None
    if _INDEX is None:
        if not load_index():
            return None
    model = _load_model()
    qvec = model.encode([query], convert_to_numpy=True)[0]
    faiss.normalize_L2(qvec.reshape(1, -1))
    D, I = _INDEX.search(qvec.reshape(1, -1), top_k)
    results = []
    for score, idx in zip(D[0], I[0]):
        if idx < 0 or idx >= len(_META):
            continue
        file, page, snippet = _META[idx]
        results.append((float(score), file, page, snippet))
    return results
