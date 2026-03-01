import streamlit as st
import os

def load_css(file_path="assets/styles.css"):
    """Loads external CSS if it exists."""
    if os.path.exists(file_path):
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def init_theme():
    """Initializes theme from URL or defaults to dark."""
    query_theme = st.query_params.get("theme")
    if "theme" not in st.session_state:
        st.session_state.theme = query_theme if query_theme else "dark"

def toggle_theme():
    """Toggles between light and dark mode."""
    new_theme = "light" if st.session_state.theme == "dark" else "dark"
    st.session_state.theme = new_theme
    st.query_params["theme"] = new_theme

def apply_theme_css():
    """Injects specific CSS overrides based on the current theme."""
    if st.session_state.theme == "light":
        st.markdown("""
        <style>
        html, body, .stApp { background:#f8fafc !important; }
        [data-testid="stAppViewContainer"] { background:#f8fafc !important; }
        h1, h2, h3, h4, h5, h6, p, span, label, div { color:#0f172a !important; }
        .top-header { background:#ffffff!important; border:1px solid rgba(0,0,0,0.08)!important; }
        .top-brand, .top-nav-link { color:#0f172a!important; }
        .home-card { background:#ffffff !important; border:1px solid rgba(0,0,0,0.08)!important; box-shadow:0 4px 12px rgba(0,0,0,0.08)!important; }
        .home-card-title { color:#0f172a!important; }
        .home-card-desc { color:#334155!important; }
        .home-what { color:#0f172a!important; }
        [data-testid="stFileUploader"] { background:#ffffff !important; border:2px dashed #cbd5e1 !important; border-radius:12px !important; padding:20px !important; }
        section[data-testid="stFileUploaderDropzone"] { background:#f8fafc !important; border:2px dashed #94a3b8 !important; }
        section[data-testid="stFileUploaderDropzone"] span { color:#0f172a !important; font-weight:600; }
        [data-testid="stSidebarNav"] { background:#ffffff !important; }
        .stButton>button { background:#2563eb!important; color:white!important; border:none!important; }
        [data-testid="stFileUploader"] button { background:#2563eb !important; color:#ffffff !important; border:none !important; padding:10px 18px !important; border-radius:8px !important; font-weight:600 !important; }
        [data-testid="stFileUploader"] button:hover { background:#1d4ed8 !important; color:#fff !important; }
        [data-testid="stFileUploader"] button span { color:white !important; }
        </style>
        """, unsafe_allow_html=True)