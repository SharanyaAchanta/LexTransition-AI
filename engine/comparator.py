
import os
import requests
import json
import hashlib
from typing import Dict, Optional

# Simple in-memory cache
from typing import Dict
AI_CACHE: Dict[str, str] = {}

# import db, mapping_logic engines
from engine import db, mapping_logic
from utils.timeout_handler import execute_with_timeout_retry, AITimeoutError

# Configurable via environment variables (Good for Docker)
OLLAMA_URL = os.environ.get("LTA_OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("LTA_OLLAMA_MODEL", "llama3")

def compare_ipc_bns(user_query: str) -> Dict[str, str]:
    """
    The Main Orchestrator:
    1. Identifies the IPC ID from the user's query (e.g., "IPC 302").
    2. Fetches the Mapping + Full Text from SQLite.
    3. Generates AI Analysis using Ollama.
    """
    # Query cleanup for consistent lookup
    clean_query = user_query.upper().replace("IPC", "").replace("SECTION", "").strip()
    
    # Mapping_logic to find the full record
    mapping = mapping_logic.map_ipc_to_bns(clean_query)
    
    if not mapping:
        return {"error": f"Section IPC {clean_query} not found in our database."}

    # Extract data from the mapping dictionary, if missing populate with defualt_mapping_
    ipc_id = clean_query
    bns_id = mapping.get('bns_section', 'Unknown')
    ipc_text = mapping.get('ipc_full_text') or "Text not available in database."
    bns_text = mapping.get('bns_full_text') or "Text not available in database."

    # Semantic Analysis
    ai_analysis = _call_ollama_diff(ipc_text, bns_text)

    return {
        "ipc_section": ipc_id,
        "ipc_text": ipc_text,
        "bns_section": bns_id,
        "bns_text": bns_text,
        "analysis": ai_analysis,
        "metadata": mapping  # Contains category, source, notes
    }
def _call_ollama_diff(ipc_text: str, bns_text: str) -> str:

    raw_key = f"{ipc_text}:{bns_text}"
    cache_key = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    # Check cache first
    if cache_key in AI_CACHE:
        print(f"[CACHE HIT] {cache_key[:40]}...")
        return AI_CACHE[cache_key]

    if not OLLAMA_URL:
        return "ERROR: AI Offline. Please check your Ollama connection."

    if "Text not available" in ipc_text or "Text not available" in bns_text:
        return "ERROR: Cannot analyze. Full legal text is missing."

    prompt = (
        f"You are a Senior Legal Analyst. Compare the following two Indian laws.\n\n"
        f"1. Old Law (IPC): {ipc_text}\n"
        f"2. New Law (BNS): {bns_text}\n\n"
        f"Task: Identify substantive changes. Ignore minor formatting differences.\n"
        f"Output specific bullet points on:\n"
        f"- Punishment Severity (Any increase?)\n"
        f"- Scope of Definition (Any new terms like 'digital'?)\n"
        f"- Bailability or Cognizance changes\n\n"
        f"Keep the response concise and strictly factual."
    )

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        def _request(timeout):
            return requests.post(
                f"{OLLAMA_URL}/api/generate",
                json=payload,
                timeout=timeout
            )

        resp = execute_with_timeout_retry(_request, retries=2, timeout=30)

        if resp.status_code == 200:
           analysis = resp.json().get("response", "No response generated.")
           print(f"[CACHE STORE] {cache_key[:40]}...")
           AI_CACHE[cache_key] = analysis
           return analysis
        
        else:
            return f"ERROR: Ollama returned status {resp.status_code}"

    except AITimeoutError:
        raise

    except requests.exceptions.ConnectionError:
        return "ERROR: Connection refused. Is Ollama running? (Try 'ollama serve')"

    except Exception as e:
        return f"ERROR: {str(e)}"

    return "Analysis failed."
