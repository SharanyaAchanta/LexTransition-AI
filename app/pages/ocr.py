"""Document OCR page for LexTransition AI."""
import streamlit as st
import os

# UI Components
from app.components.ui_helpers import copy_to_clipboard, render_agent_audio
from engine.tts_handler import tts_engine


# Universal OCR Summarizer
from engine.ocr_summarizer import summarize_with_prompt

# --- SELF-CONTAINED ENGINE CHECK ---
try:
    from engine.ocr_processor import extract_text, available_engines
    ENGINES_AVAILABLE = True
except Exception as e:
    ENGINES_AVAILABLE = False

# LLM Stub (Just like we did in Mapper)
try:
    from engine.llm import summarize as llm_summarize
except Exception:
    def llm_summarize(text, question=None): 
        return None

# --- MAIN PAGE FUNCTION ---
def render_ocr_page():
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

            if uploaded_file is None:
                st.warning("⚠ Please upload a file first.")
                st.stop()

            if not ENGINES_AVAILABLE:
                st.error("❌ OCR Engine not available.\n\n**Troubleshooting:**\n- Ensure required OCR dependencies (easyocr, pytesseract, tesseract binary) are installed.\n- Restart the app after installing dependencies.\n- Check if your environment supports OCR engines.\n")
                if st.button("🔄 Retry", use_container_width=True):
                    st.experimental_rerun()
                st.stop()

            try:
                with st.spinner("🔍 Extracting text... Please wait"):
                    raw = uploaded_file.getvalue()
                    extracted = """
FIR REGISTERED UNDER SECTION 302 IPC

You are required to appear before the court on 10/04/2026.
Failure to comply may result in legal action.
"""

                if not extracted or not extracted.strip():
                    st.warning("⚠ No text detected in the uploaded image.")
                    st.stop()

                try:
                    from engine.ocr_processor import extract_text_batch
                    with st.spinner("🔍 Extracting text... Please wait"):
                        # Use extract_text_batch for structured error handling
                        uploaded_file.seek(0)
                        results = extract_text_batch([uploaded_file])
                        filename = getattr(uploaded_file, 'name', 'uploaded_file')
                        result = results.get(filename, {})
                        if result.get('status') == 'error':
                            err_msg = result.get('error', 'Unknown error')
                            st.error(f"❌ OCR failed: {err_msg}\n\n**Troubleshooting:**\n- Check if the uploaded file is a valid image.\n- Ensure OCR dependencies are installed.\n- If using pytesseract, verify tesseract is installed and in PATH.\n- Try uploading a different file.\n")
                            if st.button("🔄 Retry", use_container_width=True):
                                st.experimental_rerun()
                            st.stop()
                        extracted = result.get('text', '')

                    if not extracted or not extracted.strip():
                        st.warning("⚠ No text detected in the uploaded image.\n\n**Troubleshooting:**\n- Ensure the image contains readable text.\n- Try increasing image quality or contrast.\n- Try a different file.")
                        if st.button("🔄 Retry", use_container_width=True):
                            st.experimental_rerun()
                        st.stop()

                    st.success("✅ Text extraction completed!")
                    st.text_area("Extracted Text", extracted, height=300)
                    copy_to_clipboard(extracted, "Copy OCR Text")

                    # ================= RISK ANALYSIS =================
                    try:
                        risk_result = summarize_with_prompt(extracted, prompt_type="risk")
                        st.markdown("### ⚠️ Legal Risk Assessment")
                        severity = risk_result.get("severity", "Unknown")
                        sections = risk_result.get("sections", [])
                        guidance = risk_result.get("guidance", "")
                        punishments = risk_result.get("punishment", [])
                        if punishments:
                            st.markdown("### ⚖️ Possible Punishment")
                            for p in punishments:
                                st.info(p)
                        if severity == "High":
                            st.error(f"🔴 Severity Level: {severity}")
                        elif severity == "Medium":
                            st.warning(f"🟠 Severity Level: {severity}")
                        else:
                            st.success(f"🟢 Severity Level: {severity}")
                        if sections:
                            st.write("**Detected Sections:**", ", ".join(sections))
                        else:
                            st.write("**Detected Sections:** None")
                        st.info(f"**Guidance:** {guidance}")
                    except Exception as e:
                        st.error(f"❌ Legal risk analysis failed: {str(e)}\n\n**Troubleshooting:**\n- Ensure the extracted text is not empty or corrupted.\n- Check if the risk analyzer engine is available.\n- Try re-running the analysis.")
                        if st.button("🔄 Retry Legal Risk Analysis", use_container_width=True):
                            st.experimental_rerun()

                    # ================= BAIL ANALYSIS =================
                    try:
                        bail_results = summarize_with_prompt(extracted, prompt_type="bail")
                        if bail_results:
                            st.markdown("### ⚖️ Bail Eligibility & Procedure")
                            for item in bail_results:
                                st.write(f"**Section {item.get('section', '')} — {item.get('description', '')}**")
                                if item.get("bailable", "") == "Non-bailable":
                                    st.error("🔴 Non-bailable")
                                else:
                                    st.success("🟢 Bailable")
                                st.write(f"Cognizable: {item.get('cognizable', '')}")
                                st.info(f"Procedure: {item.get('procedure', '')}")
                                st.write(f"Punishment: {item.get('punishment', '')}")
                                st.divider()
                    except Exception as e:
                        st.error(f"❌ Bail analysis failed: {str(e)}\n\n**Troubleshooting:**\n- Ensure the extracted text is valid.\n- Check if the bail analyzer engine is available.\n- Try re-running the analysis.")
                        if st.button("🔄 Retry Bail Analysis", use_container_width=True):
                            st.experimental_rerun()

                    # ================= DEADLINE ANALYSIS =================
                    try:
                        deadline_results = summarize_with_prompt(extracted, prompt_type="deadline")
                        if deadline_results:
                            st.markdown("### 📅 Important Dates & Deadlines")
                            for item in deadline_results:
                                status = item.get("status", "")
                                date = item.get("date", "")
                                if status == "Expired":
                                    st.error(f"❌ {date} — Expired")
                                elif status == "Urgent":
                                    st.warning(f"⚠ {date} — Urgent")
                                elif status == "Upcoming":
                                    st.info(f"📌 {date} — Upcoming")
                                else:
                                    st.write(f"{date} — Detected")
                            st.divider()
                    except Exception as e:
                        st.error(f"❌ Deadline analysis failed: {str(e)}\n\n**Troubleshooting:**\n- Ensure the extracted text is valid.\n- Check if the deadline extractor engine is available.\n- Try re-running the analysis.")
                        if st.button("🔄 Retry Deadline Analysis", use_container_width=True):
                            st.experimental_rerun()

                    # ================= PLAIN LANGUAGE SUMMARY =================
                    try:
                        summary_data = summarize_with_prompt(extracted, prompt_type="summary")
                        st.markdown("### 📝 Plain-Language Explanation")
                        if summary_data:
                            if summary_data.get("sections"):
                                st.write("**Sections Detected:**", ", ".join(summary_data["sections"]))
                            if summary_data.get("authorities"):
                                st.write("**Authorities Involved:**", ", ".join(summary_data["authorities"]))
                            if summary_data.get("action_points"):
                                st.write("**Recommended Actions:**")
                                for point in summary_data["action_points"]:
                                    st.write(f"- {point}")
                            st.info(summary_data.get("plain_summary", ""))
                    except Exception as e:
                        st.error(f"❌ Summary generation failed: {str(e)}\n\n**Troubleshooting:**\n- Ensure the extracted text is valid.\n- Check if the summarizer engine is available.\n- Try re-running the analysis.")
                        if st.button("🔄 Retry Summary Generation", use_container_width=True):
                            st.experimental_rerun()

                    try:
                        with st.spinner("🤖 Generating action items..."):
                            summary = llm_summarize(extracted, question="Action items?")
                        if summary:
                            st.success("✅ Analysis completed!")
                            st.info(f"**Action Item:** {summary}")
                            with st.spinner("🎙️ Agent is preparing action items dictation..."):
                                audio_path = tts_engine.generate_audio(summary, "temp_ocr.wav")
                                if audio_path and os.path.exists(audio_path):
                                    render_agent_audio(audio_path, title="Action Items Dictation")
                        else:
                            st.warning("⚠ AI Engine failed to generate summary.")
                    except Exception as e:
                        st.error(f"❌ AI summary/voice failed: {str(e)}\n\n**Troubleshooting:**\n- Ensure the extracted text is valid.\n- Check if the LLM or TTS engine is available.\n- Try re-running the analysis.")
                        if st.button("🔄 Retry AI Summary/Voice", use_container_width=True):
                            st.experimental_rerun()
                except Exception as e:
                    st.error(f"❌ Error during processing: {str(e)}\n\n**Troubleshooting:**\n- Check your file and try again.\n- Ensure all required dependencies are installed.\n- Restart the app if the problem persists.")
                    if st.button("🔄 Retry Processing", use_container_width=True):
                        st.experimental_rerun()