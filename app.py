import streamlit as st
import os
import glob

# MUST BE FIRST
st.set_page_config(page_title="LexTransition AI", page_icon="⚖️", layout="wide", initial_sidebar_state="expanded")

# --- Component Imports ---
from app.components.theme import init_theme, load_css, apply_theme_css
from app.components.header import render_header
from app.components.sidebar import render_sidebar
from app.components.footer import render_footer

# --- Global Definitions ---
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

# --- Initialization & Cleanup ---
def cleanup_temp_audio():
    if os.path.exists("temp_audio"):
        for audio_file in glob.glob("temp_audio/*.wav"):
            try: os.remove(audio_file)
            except Exception: pass

def get_url_page():
    try:
        val = st.query_params.get("page", None)
        return val[0] if isinstance(val, list) else val
    except Exception:
        return None

# --- Session State Setup ---
cleanup_temp_audio()
init_theme()

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

url_page = get_url_page()
if "pending_page" in st.session_state:
    st.session_state.current_page = st.session_state.pop("pending_page")
elif url_page in dict(NAV_ITEMS).keys():
    st.session_state.current_page = url_page

current_page = st.session_state.current_page

# --- Engine Pre-load (Silent) ---
try:
    from engine.rag_engine import index_pdfs
    if not st.session_state.get("pdf_indexed"):
        index_pdfs("law_pdfs")
        st.session_state.pdf_indexed = True
except Exception:
    pass # Degrade gracefully if engine fails

# --- UI Setup ---
load_css("assets/styles.css")
apply_theme_css()
render_sidebar(NAV_ITEMS)
render_header(NAV_ITEMS, current_page)

# ============================================================================
# PAGE ROUTER
# ============================================================================
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
    st.error("🚨 An unexpected error occurred.")
    st.exception(e)

# --- Footer ---
st.divider()
render_footer()