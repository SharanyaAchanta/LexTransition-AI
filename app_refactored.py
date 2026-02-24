"""LexTransition AI - Main Streamlit Application (Refactored)."""
import streamlit as st
import os
import re

# ===== THEME INITIALIZATION =====
from app.components.theme import init_theme, render_theme_toggle, apply_theme

# Initialize theme from URL params or session state
init_theme()

# Page Configuration
st.set_page_config(
    page_title="LexTransition AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- audio cleanup ---
TEMP_AUDIO_DIR = "temp_audio"
import glob
if os.path.exists(TEMP_AUDIO_DIR):
    for audio_file in glob.glob(os.path.join(TEMP_AUDIO_DIR, "*.wav")):
        try:
            os.remove(audio_file)
        except Exception:
            pass

# load css
def load_css(file_path):
    if os.path.exists(file_path):
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load external CSS file
load_css("assets/styles.css")

# Render theme toggle button
render_theme_toggle()

# Apply theme CSS
apply_theme()

# --- ENGINE LOADING WITH DEBUGGING ---
IMPORT_ERROR = None
try:
    from engine.ocr_processor import extract_text, available_engines
    from engine.mapping_logic import map_ipc_to_bns, add_mapping
    from engine.rag_engine import search_pdfs, add_pdf, index_pdfs
    from engine.db import import_mappings_from_csv, import_mappings_from_excel, export_mappings_to_json, export_mappings_to_csv
    from engine.comparator import compare_ipc_bns

    ENGINES_AVAILABLE = True
except Exception as e:
    IMPORT_ERROR = str(e)
    ENGINES_AVAILABLE = False

# LLM summarize stub
try:
    from engine.llm import summarize as llm_summarize
except Exception:
    def llm_summarize(text, question=None):
        return None

# --- INITIALIZATION ---
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# Show Engine Errors Immediately
if IMPORT_ERROR:
    st.error(f"⚠️ **System Alert:** Engines failed to load.\n\nError Details: `{IMPORT_ERROR}`")

# Index PDFs at startup if engine available
if ENGINES_AVAILABLE and not st.session_state.get("pdf_indexed"):
    try:
        index_pdfs("law_pdfs")
        st.session_state.pdf_indexed = True
    except Exception:
        pass

# --- NAVIGATION LOGIC ---
def _read_url_page():
    try:
        qp = st.query_params
        val = qp.get("page", None)
        if isinstance(val, list):
            return val[0]
        return val
    except Exception:
        return None


url_page = _read_url_page()

if "pending_page" in st.session_state:
    st.session_state.current_page = st.session_state.pop("pending_page")
else:
    from app.config import VALID_PAGES
    if url_page in VALID_PAGES:
        st.session_state.current_page = url_page

# --- RENDER SIDEBAR AND HEADER ---
from app.components import render_sidebar, render_header
render_sidebar()
render_header()

current_page = st.session_state.current_page

try:
    # --- PAGE ROUTING ---
    from app.pages import (
        render_home,
        render_mapper,
        render_ocr,
        render_fact_checker,
        render_settings,
        render_faq,
        render_privacy,
        render_community,
    )
    from app.components import render_footer
    
    if current_page == "Home":
        render_home()
    elif current_page == "Mapper":
        render_mapper(ENGINES_AVAILABLE)
    elif current_page == "OCR":
        render_ocr(ENGINES_AVAILABLE)
    elif current_page == "Fact":
        render_fact_checker(ENGINES_AVAILABLE)
    elif current_page == "Settings":
        render_settings(ENGINES_AVAILABLE)
    elif current_page == "FAQ":
        render_faq()
    elif current_page == "Privacy":
        render_privacy()
    elif current_page == "Community":
        render_community()
    
    # --- RENDER FOOTER ---
    render_footer()

except Exception as e:
    st.error("🚨 An unexpected error occurred.")
    st.exception(e)
