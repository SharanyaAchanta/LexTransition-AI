"""Theme management component for LexTransition AI."""
import streamlit as st


def init_theme():
    """Initialize theme from URL params or session state."""
    query_theme = st.query_params.get("theme")
    
    if "theme" not in st.session_state:
        if query_theme:
            st.session_state.theme = query_theme
        else:
            st.session_state.theme = "dark"
    
    return st.session_state.theme


def toggle_theme():
    """Toggle between dark and light themes."""
    new_theme = "light" if st.session_state.theme == "dark" else "dark"
    st.session_state.theme = new_theme
    st.query_params["theme"] = new_theme


def render_theme_toggle():
    """Render the theme toggle button."""
    col1, col2 = st.columns([10, 1])
    with col2:
        icon = "🌙" if st.session_state.theme == "dark" else "☀️"
        if st.button(icon):
            toggle_theme()
            st.rerun()


def apply_theme():
    """Apply theme-specific CSS styles."""
    if st.session_state.theme == "light":
        st.markdown("""
        <style>

        html, body, .stApp {
            background:#f8fafc !important;
        }

        [data-testid="stAppViewContainer"]{
            background:#f8fafc !important;
        }

        /* TEXT */
        h1,h2,h3,h4,h5,h6,p,span,label,div{
            color:#0f172a !important;
        }

        /* HEADER */
        .top-header{
            background:#ffffff!important;
            border:1px solid rgba(0,0,0,0.08)!important;
        }

        .top-brand,.top-nav-link{
            color:#0f172a!important;
        }

        /* HOME CARDS */
        .home-card{
            background:#ffffff !important;
            border:1px solid rgba(0,0,0,0.08)!important;
            box-shadow:0 4px 12px rgba(0,0,0,0.08)!important;
        }

        .home-card-title{color:#0f172a!important;}
        .home-card-desc{color:#334155!important;}
        .home-what{color:#0f172a!important;}

        /* OCR UPLOAD BOX */
        [data-testid="stFileUploader"]{
            background:#ffffff !important;
            border:2px dashed #cbd5e1 !important;
            border-radius:12px !important;
            padding:20px !important;
        }

        section[data-testid="stFileUploaderDropzone"]{
            background:#f8fafc !important;
            border:2px dashed #94a3b8 !important;
        }

        section[data-testid="stFileUploaderDropzone"] span{
            color:#0f172a !important;
            font-weight:600;
        }

        /* SIDEBAR */
        [data-testid="stSidebarNav"]{
            background:#ffffff !important;
        }

        /* BUTTON */
        .stButton>button{
            background:#2563eb!important;
            color:white!important;
            border:none!important;
        }

        [data-testid="stFileUploader"] button {
            background:#2563eb !important;
            color:#ffffff !important;
            border:none !important;
            padding:10px 18px !important;
            border-radius:8px !important;
            font-weight:600 !important;
        }
        
        /* hover */
        [data-testid="stFileUploader"] button:hover {
            background:#1d4ed8 !important;
            color:#fff !important;
        }
        
        /* remove black default */
        [data-testid="stFileUploader"] button span{
            color:white !important;
        }

        </style>
        """, unsafe_allow_html=True)
