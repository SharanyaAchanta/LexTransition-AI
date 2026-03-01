"""Home page for LexTransition AI."""
import streamlit as st

def render_home_page():
    """Render the Home page."""
    st.markdown('<div class="home-header">', unsafe_allow_html=True)
    st.markdown('<div class="home-title">⚖️ LexTransition AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="home-subtitle">'
        'Your offline legal assistant powered by AI. Analyze documents, map sections, and get instant legal insights—no internet required.'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="home-what">What do you want to do?</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown(f"""
        <a class="home-card" href="?page=Mapper&theme={st.session_state.theme}" target="_self">
            <div class="home-card-header">
                <span class="home-card-icon">🔄</span>
                <div class="home-card-title">IPC → BNS Mapper</div>
            </div>
            <div class="home-card-desc">Quickly find the new BNS equivalent of any IPC section.</div>
            <div class="home-card-btn"><span>Open Mapper</span><span>›</span></div>
        </a>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <a class="home-card" href="?page=OCR&theme={st.session_state.theme}" target="_self">
            <div class="home-card-header">
                <span class="home-card-icon">📄</span>
                <div class="home-card-title">Document OCR</div>
            </div>
            <div class="home-card-desc">Extract text and action points from documents.</div>
            <div class="home-card-btn"><span>Upload & Analyze</span><span>›</span></div>
        </a>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col3, col4 = st.columns(2, gap="large")
    with col3:
        st.markdown("""
        <a class="home-card" href="?page=Fact" target="_self">
            <div class="home-card-header">
                <span class="home-card-icon">📚</span>
                <div class="home-card-title">Legal Research</div>
            </div>
            <div class="home-card-desc">Search and analyze case law and statutes.</div>
            <div class="home-card-btn"><span>Start Research</span><span>›</span></div>
        </a>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <a class="home-card" href="?page=Settings" target="_self">
            <div class="home-card-header">
                <span class="home-card-icon">⚙️</span>
                <div class="home-card-title">Settings</div>
            </div>
            <div class="home-card-desc">Configure engines and offline settings.</div>
            <div class="home-card-btn"><span>Configure</span><span>›</span></div>
        </a>
        """, unsafe_allow_html=True)
