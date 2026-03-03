import streamlit as st

def render_sidebar(nav_items):
    """Renders the mobile sidebar navigation."""
    with st.sidebar:
        st.markdown('<div class="sidebar-title">LexTransition AI</div>', unsafe_allow_html=True)
        for page, label in nav_items:
            if st.button(label, key=f"side_{page}", use_container_width=True):
                st.session_state.current_page = page
                st.rerun()
        st.markdown('<div class="sidebar-badge">Offline Mode • V1.0</div>', unsafe_allow_html=True)