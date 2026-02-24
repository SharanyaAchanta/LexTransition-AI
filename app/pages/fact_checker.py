"""Fact Checker page for LexTransition AI."""
import os
import streamlit as st
from app.components.tts_helper import render_agent_audio


def _safe_filename(name: str, default: str) -> str:
    """Generate a safe filename."""
    import re
    _SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]+")
    base = os.path.basename(name or "").strip().replace("\x00", "")
    if not base:
        return default
    safe = _SAFE_FILENAME_RE.sub("_", base).strip("._")
    return safe or default


def render(ENGINES_AVAILABLE):
    """Render the Fact Checker page.
    
    Args:
        ENGINES_AVAILABLE: Boolean indicating if engines are available
    """
    st.markdown("## 📚 Grounded Fact Checker")
    st.markdown("Ask a legal question to verify answers with citations from official PDFs.")
    st.divider()
    
    col1, col2 = st.columns([2, 1])
    with col1:
        user_question = st.text_input("Question", placeholder="e.g., penalty for cheating?")
    with col2:
        verify_btn = st.button("📖 Verify", use_container_width=True)
    
    with st.expander("Upload Law PDFs"):
        uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded_pdf and ENGINES_AVAILABLE:
            from engine.rag_engine import add_pdf
            save_dir = "law_pdfs"
            os.makedirs(save_dir, exist_ok=True)
            path = os.path.join(save_dir, _safe_filename(uploaded_pdf.name, "doc.pdf"))
            with open(path, "wb") as f:
                f.write(uploaded_pdf.read())
            add_pdf(path)
            st.success(f"Added {uploaded_pdf.name}")

    if user_question and verify_btn:
        if ENGINES_AVAILABLE:
            from engine.rag_engine import search_pdfs
            from engine.tts_handler import tts_engine
            
            res = search_pdfs(user_question)
            if res:
                st.markdown(res)
                
                # --- TTS INTEGRATION START (Fact Checker) ---
                with st.spinner("🎙️ Agent is preparing the verbal citation..."):
                    # Pass the 'res' string directly to the audio engine
                    audio_path = tts_engine.generate_audio(res, "temp_fact_check.wav")
                    if audio_path and os.path.exists(audio_path):
                        render_agent_audio(audio_path, title="Legal Fact Dictation")
                # --- TTS INTEGRATION END ---
                
            else:
                st.info("No citations found.")
        else:
            st.error("RAG Engine offline.")
