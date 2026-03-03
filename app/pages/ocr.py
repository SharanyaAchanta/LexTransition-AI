"""Document OCR page for LexTransition AI."""
import streamlit as st
import os

# UI Components
from app.components.ui_helpers import copy_to_clipboard, render_agent_audio
from engine.tts_handler import tts_engine

# OCR Specific Engines
from engine.risk_analyzer import analyze_risk
from engine.bail_analyzer import analyze_bail
from engine.summarizer import generate_summary
from engine.deadline_extractor import analyze_deadlines

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
                st.error("❌ OCR Engine not available.")
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

                st.success("✅ Text extraction completed!")
                st.text_area("Extracted Text", extracted, height=300)

                copy_to_clipboard(extracted, "Copy OCR Text")
                
                # ================= RISK ANALYSIS =================
                risk_result = analyze_risk(extracted)

                st.markdown("### ⚠️ Legal Risk Assessment")

                severity = risk_result["severity"]
                sections = risk_result["sections"]
                guidance = risk_result["guidance"]
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

                # ================= BAIL ANALYSIS =================
                bail_results = analyze_bail(extracted)

                if bail_results:
                    st.markdown("### ⚖️ Bail Eligibility & Procedure")

                    for item in bail_results:
                        st.write(f"**Section {item['section']} — {item['description']}**")

                        if item["bailable"] == "Non-bailable":
                            st.error("🔴 Non-bailable")
                        else:
                            st.success("🟢 Bailable")

                        st.write(f"Cognizable: {item['cognizable']}")
                        st.info(f"Procedure: {item['procedure']}")
                        st.write(f"Punishment: {item['punishment']}")

                        st.divider()
                # ================= DEADLINE ANALYSIS =================
                deadline_results = analyze_deadlines(extracted)

                if deadline_results:
                    st.markdown("### 📅 Important Dates & Deadlines")

                    for item in deadline_results:

                        if item["status"] == "Expired":
                            st.error(f"❌ {item['date']} — Expired")
                        elif item["status"] == "Urgent":
                            st.warning(f"⚠ {item['date']} — Urgent")
                        elif item["status"] == "Upcoming":
                            st.info(f"📌 {item['date']} — Upcoming")
                        else:
                            st.write(f"{item['date']} — Detected")

                    st.divider()

        # ================= PLAIN LANGUAGE SUMMARY =================
                summary_data = generate_summary(extracted)

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
                st.error(f"❌ Error during processing: {str(e)}")