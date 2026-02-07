"""
Local LLM adapter (optional).
- If LTA_OLLAMA_URL is set, it will POST prompt to that endpoint and return text.
- If not configured, falls back to a lightweight extractive summary (first N sentences).
"""
import os

OLLAMA_URL = os.environ.get("LTA_OLLAMA_URL")  # e.g., http://localhost:11434
OLLAMA_MODEL = os.environ.get("LTA_OLLAMA_MODEL", "llama2")

def _extractive_summary(text: str, max_sentences: int = 3) -> str:
    # naive sentence split
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
    if not sentences:
        return ""
    return ". ".join(sentences[:max_sentences]) + (". " if len(sentences) > 0 else "")

def summarize(text: str, question: str = None) -> str:
    if OLLAMA_URL:
        try:
            import requests  # local import to keep dependency optional
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": f"Summarize the following legal text in plain language:{' Question: '+question if question else ''}\n\n{text}"
            }
            resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=15)
            if resp.ok:
                data = resp.json()
                # Many Ollama responses include 'text' in result
                return data.get("text") or str(data)
        except Exception:
            pass
    # fallback
    return _extractive_summary(text)
