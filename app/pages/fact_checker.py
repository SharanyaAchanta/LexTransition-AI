"""Fact Checker page for LexTransition AI."""
import streamlit as st
import os
import re

# UI Components & Audio Handlers
from app.components.ui_helpers import render_agent_audio
from engine.tts_handler import tts_engine
from engine.stt_handler import get_stt_engine
from streamlit_mic_recorder import mic_recorder

# --- SELF-CONTAINED ENGINE CHECK ---
try:
    from engine.rag_engine import search_pdfs, add_pdf
    ENGINES_AVAILABLE = True
except Exception:
    ENGINES_AVAILABLE = False

def _safe_filename(name: str, default: str) -> str:
    """Generate a safe filename."""
    import re
    _SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]+")
    base = os.path.basename(name or "").strip().replace("\x00", "")
    if not base:
        return default
    safe = _SAFE_FILENAME_RE.sub("_", base).strip("._")
    return safe or default

def clean_text_for_tts(text: str) -> str:
        """Removes markdown formatting so the TTS sounds natural."""
        import re
        text = re.sub(r'[*_]{1,3}', '', text)
        text = re.sub(r'>\s?', '', text)
        text = text.replace('\n', ' ')
        return text.strip()

def render_fact_checker_page():
    """Render the Fact Checker page.
    
    Args:
        ENGINES_AVAILABLE: Boolean indicating if engines are available
    """
    
        
    st.markdown("## 📚 Grounded Fact Checker")
    st.markdown("Ask a legal question to verify answers with citations from official PDFs.")
    st.divider()
    
    # Input Section Wrapper
    st.markdown('<div class="mapper-wrap">', unsafe_allow_html=True)
    
    # --- 3-column layout: Input | Mic | Search ---
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        # Bind the value to our session state so Voice Input auto-fills this box
        user_question = st.text_input(
            "Question", 
            value=st.session_state.get('fact_search_val', ''),
            placeholder="e.g., penalty for cheating?",
            label_visibility="collapsed"
        )
        
    with col2:
        # --- STT Integration Widget (Input) ---
        audio_dict = mic_recorder(
            start_prompt="🎙️ Speak",
            stop_prompt="🛑 Stop",
            key='fact_mic',
            use_container_width=True
        )

    with col3:
        verify_btn = st.button("📖 Verify", use_container_width=True)

    # --- Process Audio Input ---
    audio_val = audio_dict['bytes'] if audio_dict else None
    
    # Process the audio only once
    if audio_val and audio_val != st.session_state.get("last_audio_fact"):
        st.session_state["last_audio_fact"] = audio_val 
        
        temp_path = "temp_audio/fact_audio.wav"
        os.makedirs("temp_audio", exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(audio_val)
            
        with st.spinner("🎙️ Agent is listening..."):
            stt_engine = get_stt_engine() 
            text = stt_engine.transcribe_audio(temp_path)
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
            # Standardize spoken numbers to digits so the search engine handles them better
            word_to_num = {
                r'\bone\b': '1', r'\btwo\b': '2', r'\bthree\b': '3', 
                r'\bfour\b': '4', r'\bfive\b': '5', r'\bsix\b': '6', 
                r'\bseven\b': '7', r'\beight\b': '8', r'\bnine\b': '9', r'\bten\b': '10'
            }
            voice_query = text.strip()
            for word, num in word_to_num.items():
                voice_query = re.sub(word, num, voice_query, flags=re.IGNORECASE)
                
            st.session_state['fact_search_val'] = voice_query
            st.session_state['fact_auto_search'] = True 
            st.rerun()

    # --- Auto-Search Trigger ---
    if st.session_state.get('fact_auto_search'):
        verify_btn = True
        st.session_state['fact_auto_search'] = False

    # --- Upload PDF Section ---
    with st.expander("Upload Law PDFs"):
        uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded_pdf and ENGINES_AVAILABLE:
            save_dir = "law_pdfs"
            os.makedirs(save_dir, exist_ok=True)
            path = os.path.join(save_dir, _safe_filename(uploaded_pdf.name, "doc.pdf"))
            with open(path, "wb") as f: f.write(uploaded_pdf.read())
            add_pdf(path)
            st.success(f"Added {uploaded_pdf.name}")

    # --- Search & TTS Output Logic ---
    if user_question and verify_btn:
        if ENGINES_AVAILABLE:
            with st.spinner("Searching documents..."):
                res = search_pdfs(user_question.strip())
                
                if res:
                    # Display the visual text result
                    st.markdown(res)
                    
                    # --- TTS INTEGRATION START (Output) ---
                    with st.spinner("🎙️ Agent is preparing the verbal citation..."):
                        # Clean the markdown so the TTS agent reads it smoothly
                        clean_res = clean_text_for_tts(res) 
                        audio_path = tts_engine.generate_audio(clean_res, "temp_fact_check.wav")
                        
                        if audio_path and os.path.exists(audio_path):
                            render_agent_audio(audio_path, title="Legal Fact Dictation")
                    # --- TTS INTEGRATION END ---
                    
                else:
                    st.info("No citations found.")
        else:
            st.error("RAG Engine offline.")
