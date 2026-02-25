"""Settings page for LexTransition AI."""


def render(ENGINES_AVAILABLE):
    """Render the Settings/About page.
    
    Args:
        ENGINES_AVAILABLE: Boolean indicating if engines are available
    """
    st.markdown("## ⚙️ Settings / About")
    st.divider()
    st.markdown("""
    ### Application Information
    - **Version:** 1.0.0
    - **Backend:** Python + Streamlit
    - **Intelligence:** Local LLM (Ollama) + Law Mapper Engine
    
    ### Engine Status
    """)
    if ENGINES_AVAILABLE:
        st.success("✅ Legal Engines: Online")
    else:
        st.error("❌ Legal Engines: Offline")
    
    st.markdown("### User Controls")
    if st.button("Clear Cache & Rerun"):
        st.session_state.clear()
        st.rerun()
