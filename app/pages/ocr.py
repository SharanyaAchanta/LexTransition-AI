"""Document OCR page for LexTransition AI."""
import streamlit as st
from app.components.tts_helper import render_agent_audio


def render(ENGINES_AVAILABLE):
    """Render the Document OCR page.
    
    Args:
        ENGINES_AVAILABLE: Boolean indicating if engines are available
    """
    st.markdown("## 🖼️ Document OCR")
    st.markdown("Extract text and key action items from legal notices, FIRs, and scanned documents.")
    st.divider()
    
    col1, col2 = st.columns([1, 1])
    with col1:
        uploaded_file = st.file_uploader("Upload (FIR/Notice)", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        if uploaded_file:
            st.image(uploaded_file, width=500)
    
    with col2:
        if st.button("🔧 Extract & Analyze", use_container_width=True):
            # Fixed the indentation for this entire block so it executes inside the button click!
            if uploaded_file is None:
                st.warning("⚠ Please upload a file first.")
                st.stop()

            if not ENGINES_AVAILABLE:
                st.error("❌ OCR Engine not available.")
                st.stop()

            try:
                from engine.ocr_processor import extract_text
                from engine.llm import summarize as llm_summarize
                from engine.tts_handler import tts_engine
                
                with st.spinner("🔍 Extracting text... Please wait"):
                    raw = uploaded_file.getvalue()   # <-- change here
                    extracted = extract_text(raw)

                if not extracted or not extracted.strip():
                    st.warning("⚠ No text detected in the uploaded image.")
                    st.stop()

                st.success("✅ Text extraction completed!")
                st.text_area("Extracted Text", extracted, height=300)

                with st.spinner("🤖 Generating action items..."):
                    summary = llm_summarize(extracted, question="Action items?")

                if summary:
                    st.success("✅ Analysis completed!")
                    st.info(f"**Action Item:** {summary}")

                    # --- TTS INTEGRATION START (OCR Action Items) ---
                    with st.spinner("🎙️ Agent is preparing action items dictation..."):
                        audio_path = tts_engine.generate_audio(summary, "temp_ocr.wav")
                        if audio_path and __import__('os').path.exists(audio_path):
                            render_agent_audio(audio_path, title="Action Items Dictation")
                    # --- TTS INTEGRATION END ---

                else:
                    st.error("❌ OCR Engine not available.")
            except Exception as e:
                st.error(f"❌ Error during OCR processing: {str(e)}")
