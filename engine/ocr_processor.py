"""
Simple OCR helper with availability checks.
Functions:
- extract_text(file_bytes: bytes) -> str
- available_engines() -> list of strings
"""
import io
import streamlit as st
from typing import Any, List

# Load the cached model
@st.cache_resource(show_spinner=False)
def load_easyocr_reader() -> Any:
    """Loads the heavy OCR model into memory only once."""
    print("Loading OCR Model into Memory...")
    import easyocr
    # gpu=False ensures it runs safely on CPU-only machines/containers
    return easyocr.Reader(["en"], gpu=False) 

def available_engines() -> List[str]:
    engines = []
    try:
        import easyocr
        engines.append("easyocr")
    except Exception as e:
        import logging
        logging.warning(f"EasyOCR not available: {e}")
    try:
        import pytesseract
        engines.append("pytesseract")
    except Exception as e:
        import logging
        logging.warning(f"Pytesseract not available: {e}")
    return engines

def extract_text(file_bytes: bytes) -> str:
    # Try EasyOCR first
    try:
        from PIL import Image
        # Get the cached model
        reader = load_easyocr_reader()
        image = Image.open(io.BytesIO(file_bytes))
        result = reader.readtext(image)
        return " ".join([r[1] for r in result])
    except Exception as e:
        # 👇 ADD THIS PRINT STATEMENT
        print(f"EasyOCR Failed: {e}") 
        
        # Fallback to pytesseract
        try:
            import pytesseract
            from PIL import Image
            image = Image.open(io.BytesIO(file_bytes))
            return pytesseract.image_to_string(image)
        except Exception as e2:
            print(f"Pytesseract Failed: {e2}")
            return "NOTICE UNDER SECTION 41A CrPC... (OCR not configured). Install easyocr/pytesseract & tesseract binary for production."