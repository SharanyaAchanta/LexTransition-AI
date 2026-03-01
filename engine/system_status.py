import os


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