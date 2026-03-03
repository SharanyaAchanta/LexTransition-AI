import streamlit as st
import os
import glob
import re
import base64

# ==============================
# MUST BE FIRST
# ==============================
st.set_page_config(
    page_title="LexTransition AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================
# COMPONENT IMPORTS
# ==============================
from app.components.theme import init_theme, load_css, apply_theme_css
from app.components.header import render_header
from app.components.sidebar import render_sidebar
from app.components.footer import render_footer

# ==============================
# ENGINE LOADING
# ==============================
IMPORT_ERROR = None
try:
    from engine.ocr_processor import extract_text, available_engines
    from engine.mapping_logic import map_ipc_to_bns, add_mapping
    from engine.rag_engine import search_pdfs, add_pdf, index_pdfs
    from engine.db import (
        import_mappings_from_csv,
        import_mappings_from_excel,
        export_mappings_to_json,
        export_mappings_to_csv,
    )
    from engine.comparator import compare_ipc_bns
    from engine import glossary as glossary_engine
    ENGINES_AVAILABLE = True
except Exception as e:
    IMPORT_ERROR = str(e)
    ENGINES_AVAILABLE = False

# LLM fallback
try:
    from engine.llm import summarize as llm_summarize
except Exception:
    def llm_summarize(text, question=None):
        return None

# ==============================
# CONTEXT MEMORY
# ==============================
if "context_memory" not in st.session_state:
    st.session_state.context_memory = ""

def store_context(text: str):
    if text:
        st.session_state.context_memory = text

def clear_context():
    st.session_state.context_memory = ""

# ==============================
# CLEANUP TEMP AUDIO
# ==============================
def cleanup_temp_audio():
    if os.path.exists("temp_audio"):
        for f in glob.glob("temp_audio/*.wav"):
            try:
                os.remove(f)
            except Exception:
                pass

cleanup_temp_audio()

# ==============================
# NAVIGATION SETUP
# ==============================
NAV_ITEMS = [
    ("Home", "Home"),
    ("Mapper", "IPC -> BNS Mapper"),
    ("OCR", "Document OCR"),
    ("Glossary", "Legal Glossary"),
    ("Fact", "Fact Checker"),
    ("Community", "Community Hub"),
    ("Settings", "Settings / About"),
    ("FAQ", "FAQ"),
    ("Privacy", "Privacy Policy"),
]

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

def get_url_page():
    try:
        val = st.query_params.get("page", None)
        return val[0] if isinstance(val, list) else val
    except Exception:
        return None

url_page = get_url_page()

if "pending_page" in st.session_state:
    st.session_state.current_page = st.session_state.pop("pending_page")
elif url_page in dict(NAV_ITEMS):
    st.session_state.current_page = url_page

current_page = st.session_state.current_page

# ==============================
# INITIAL PDF INDEXING
# ==============================
if ENGINES_AVAILABLE and not st.session_state.get("pdf_indexed"):
    try:
        index_pdfs("law_pdfs")
        st.session_state.pdf_indexed = True
    except Exception:
        pass

# ==============================
# UI SETUP
# ==============================
load_css("assets/styles.css")
init_theme()
apply_theme_css()
render_sidebar(NAV_ITEMS)
render_header(NAV_ITEMS, current_page)

if IMPORT_ERROR:
    st.error(f"⚠️ Engines failed to load.\n\nError: `{IMPORT_ERROR}`")

# ==============================
# PAGE ROUTER
# ==============================
try:

    if current_page == "Home":
        from app.pages.home import render_home_page
        render_home_page()

    elif current_page == "Mapper":
        from app.pages.mapper import render_mapper_page
        render_mapper_page()

    elif current_page == "OCR":
        from app.pages.ocr import render_ocr_page
        render_ocr_page()

    elif current_page == "Glossary":
        from app.pages.glossary import render_glossary_page
        render_glossary_page()

    elif current_page == "Fact":
        from app.pages.fact_checker import render_fact_checker_page
        render_fact_checker_page()

    elif current_page == "Community":
        from app.pages.community import render_community_page
        render_community_page()

    elif current_page == "Settings":
        from app.pages.settings import render_settings_page
        render_settings_page()

    elif current_page == "FAQ":
        from app.pages.faq import render_faq_page
        render_faq_page()

    elif current_page == "Privacy":
        from app.pages.privacy import render_privacy_page
        render_privacy_page()

    else:
        st.error("Page not found.")

except Exception as e:
    st.error("🚨 Unexpected error occurred.")
    st.exception(e)

# ==============================
# FOOTER
# ==============================
st.divider()
render_footer()