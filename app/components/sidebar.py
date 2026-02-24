"""Sidebar navigation component for LexTransition AI."""
import streamlit as st
from app.config import NAV_ITEMS


def render_sidebar():
    """Render the sidebar navigation for mobile."""
    with st.sidebar:
        st.markdown('<div class="sidebar-title">LexTransition AI</div>', unsafe_allow_html=True)
        for page, label in NAV_ITEMS:
            if st.button(label, key=f"side_{page}", use_container_width=True):
                st.session_state.current_page = page
                st.rerun()
        st.markdown('<div class="sidebar-badge">Offline Mode • V1.0</div>', unsafe_allow_html=True)
