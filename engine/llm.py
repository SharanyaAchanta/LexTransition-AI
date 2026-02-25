"""
Local LLM adapter (optional).
- If LTA_OLLAMA_URL is set, it will POST prompt to that endpoint and return text.
- If not configured, falls back to a lightweight extractive summary.
"""
import os
import json
from typing import Optional

from utils.timeout_handler import execute_with_timeout_retry, AITimeoutError

OLLAMA_URL: Optional[str] = os.environ.get("LTA_OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.environ.get("LTA_OLLAMA_MODEL", "llama2")


def _extractive_summary(text: str, max_sentences: int = 3) -> str:
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
    if not sentences:
        return ""
    return ". ".join(sentences[:max_sentences]) + "."


def summarize(text: str, question: Optional[str] = None) -> str:
    if OLLAMA_URL:
        try:
            import requests

            payload = {
                "model": OLLAMA_MODEL,
                "prompt": (
                    f"Summarize the following legal text in plain language:"
                    f"{' Question: ' + question if question else ''}\n\n{text}"
                ),
                "stream": False,
            }

            def _call_ollama(timeout):
                return requests.post(
                    f"{OLLAMA_URL}/api/generate",
                    json=payload,
                    timeout=timeout,
                )

            resp = execute_with_timeout_retry(_call_ollama)

            if resp and resp.ok:
                try:
                    data = resp.json()
                    return data.get("response") or data.get("text") or str(data)
                except Exception:
                    combined = []
                    for line in resp.text.splitlines():
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            obj = json.loads(line)
                        except Exception:
                            continue
                        chunk = obj.get("response") or obj.get("text")
                        if chunk:
                            combined.append(str(chunk))
                    if combined:
                        return "".join(combined).strip()

        except AITimeoutError:
            raise  # Let app.py handle UI message

        except Exception:
            pass

    return _extractive_summary(text)