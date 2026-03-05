import os
import psutil
import shutil

def get_resource_usage():
    """Return system resource usage."""
    try:
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = shutil.disk_usage("/")
        return {
            "cpu": cpu,
            "ram_percent": memory.percent,
            "ram_used_gb": round(memory.used / (1024**3), 2),
            "ram_total_gb": round(memory.total / (1024**3), 2),
            "disk_percent": round((disk.used / disk.total) * 100, 2),
            "disk_used_gb": round(disk.used / (1024**3), 2),
            "disk_total_gb": round(disk.total / (1024**3), 2),
        }
    except Exception:
        return None

def check_mapping_db():
    return os.path.exists("mapping_db.sqlite") or os.path.exists("mapping_db.json")

def check_ocr():
    try:
        from engine.ocr_processor import extract_text
        return True
    except Exception:
        return False

def check_rag():
    try:
        from engine.rag_engine import search_pdfs
        return True
    except Exception:
        return False

def check_llm():
    try:
        from engine.llm import summarize
        return True
    except Exception:
        return False

def check_voice():
    try:
        from engine.tts_handler import tts_engine
        return True
    except Exception:
        return False

def get_system_status():
    return {
        "Mapping Database": check_mapping_db(),
        "OCR Engine": check_ocr(),
        "RAG Search": check_rag(),
        "LLM Engine": check_llm(),
        "Voice Modules": check_voice(),
    }
