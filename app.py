import streamlit as st
# Trigger reload for CSS update (Nav 2-line + Button Fix)
import os
import html as html_lib
import re
import time
import base64
# Import TTS engine 
from engine.tts_handler import tts_engine

# Page Configuration
st.set_page_config(
    page_title="LexTransition AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

import glob

# --- audio cleanup ---
TEMP_AUDIO_DIR = "temp_audio"
if os.path.exists(TEMP_AUDIO_DIR):
    for audio_file in glob.glob(os.path.join(TEMP_AUDIO_DIR, "*.wav")):
        try:
            os.remove(audio_file)
        except Exception:
            pass # File might be playing 

# load css
def load_css(file_path):
    if os.path.exists(file_path):
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load external CSS file
load_css("assets/styles.css")


def apply_theme(theme_mode: str):
    """Apply lightweight theme overrides without changing layout structure."""
    is_light = theme_mode == "light"

    if is_light:
        theme_css = """
        <style>
        :root {
            --app-bg: #f6f8fb;
            --surface-bg: #ffffff;
            --text-color: #1f2937;
            --muted-text: #4b5563;
            --border-color: #d1d5db;
        }

        [data-testid="stAppViewContainer"],
        [data-testid="stSidebar"] {
            background: var(--app-bg);
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stSidebar"] > div {
            background: var(--surface-bg);
            border-right: 1px solid var(--border-color);
        }

        [data-testid="stAppViewContainer"] .main,
        [data-testid="stAppViewContainer"] .block-container {
            background: transparent;
            color: var(--text-color);
        }

        [data-testid="stMarkdownContainer"],
        [data-testid="stText"],
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
            color: var(--text-color);
        }

        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea,
        [data-testid="stSelectbox"] > div,
        [data-testid="stFileUploader"] section {
            background: var(--surface-bg);
            color: var(--text-color);
            border-color: var(--border-color);
        }

        [data-testid="stButton"] > button,
        [data-testid="stDownloadButton"] > button {
            border: 1px solid var(--border-color);
            background: var(--surface-bg);
            color: var(--text-color);
        }

        .sidebar-badge,
        .top-chip,
        .top-credit {
            color: var(--muted-text) !important;
        }
        </style>
        """
    else:
        theme_css = """
        <style>
        :root {
            --app-bg: #0e1117;
            --surface-bg: #111827;
            --text-color: #f3f4f6;
            --border-color: rgba(255, 255, 255, 0.16);
        }

        [data-testid="stAppViewContainer"],
        [data-testid="stSidebar"] {
            background: var(--app-bg);
        }

        [data-testid="stSidebar"] > div {
            background: var(--surface-bg);
            border-right: 1px solid var(--border-color);
        }

        [data-testid="stButton"] > button,
        [data-testid="stDownloadButton"] > button {
            border-color: var(--border-color);
        }
        </style>
        """

    st.markdown(theme_css, unsafe_allow_html=True)


if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"

apply_theme(st.session_state.theme_mode)

# --- ENGINE LOADING WITH DEBUGGING ---
IMPORT_ERROR = None
try:
    from engine.ocr_processor import extract_text, available_engines
    from engine.mapping_logic import map_ipc_to_bns, add_mapping
    from engine.rag_engine import search_pdfs, add_pdf, index_pdfs
    from engine.db import import_mappings_from_csv, import_mappings_from_excel, export_mappings_to_json, export_mappings_to_csv

    # Import the Semantic Comparator Engine
    from engine.comparator import compare_ipc_bns

    ENGINES_AVAILABLE = True
except Exception as e:
    # [FIX 1] Capture the specific error so we can show it
    IMPORT_ERROR = str(e)
    ENGINES_AVAILABLE = False

# LLM summarize stub
try:
    from engine.llm import summarize as llm_summarize
except Exception:
    def llm_summarize(text, question=None):
        return None

# --- INITIALIZATION ---
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# [FIX 1] Show Engine Errors Immediately
if IMPORT_ERROR:
    st.error(f"⚠️ **System Alert:** Engines failed to load.\n\nError Details: `{IMPORT_ERROR}`")

# Index PDFs at startup if engine available
if ENGINES_AVAILABLE and not st.session_state.get("pdf_indexed"):
    try:
        index_pdfs("law_pdfs")
        st.session_state.pdf_indexed = True
    except Exception:
        pass

# --- NAVIGATION LOGIC ---

_SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


def _safe_filename(name: str, default: str) -> str:
    base = os.path.basename(name or "").strip().replace("\x00", "")
    if not base:
        return default
    safe = _SAFE_FILENAME_RE.sub("_", base).strip("._")
    return safe or default

# render the agent
def render_agent_audio(audio_path, title="🎙️ AI Agent Dictation"):
    """Wraps the audio player in a premium custom HTML card."""
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()
    
    # Encode the audio so we can embed it directly in the HTML
    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
    
    # Custom CSS and HTML structure using flexible rgba colors for dark/light mode compatibility
    custom_html = f"""
    <div style="
        border: 1px solid rgba(128, 128, 128, 0.3);
        border-radius: 8px;
        padding: 12px 15px;
        background: rgba(128, 128, 128, 0.05);
        display: flex;
        align-items: center;
        margin-top: 10px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    ">
        <div style="margin-right: 15px; font-size: 1.8em;">🤖</div>
        <div style="flex-grow: 1;">
            <div style="font-size: 0.9em; font-weight: 600; opacity: 0.8; margin-bottom: 6px; font-family: sans-serif;">
                {title}
            </div>
            <audio controls style="width: 100%; height: 35px; border-radius: 4px; outline: none;">
                <source src="data:audio/wav;base64,{audio_base64}" type="audio/wav">
                Your browser does not support the audio element.
            </audio>
        </div>
    </div>
    """
    st.markdown(custom_html, unsafe_allow_html=True)

# reading the page url
def _read_url_page():
    try:
        qp = st.query_params
        try:
            val = qp.get("page", None)
        except Exception:
            try:
                val = dict(qp).get("page", None)
            except Exception:
                val = None
        if isinstance(val, list):
            return val[0]
        return val
    except Exception:
        qp = st.experimental_get_query_params()
        return qp.get("page", [None])[0] if qp else None


url_page = _read_url_page()

if "pending_page" in st.session_state:
    st.session_state.current_page = st.session_state.pop("pending_page")
else:
    if url_page in {"Home", "Mapper", "OCR", "Fact", "Settings", "Privacy", "FAQ"}:
        st.session_state.current_page = url_page

nav_items = [
    ("Home", "Home"),
    ("Mapper", "IPC -> BNS Mapper"),
    ("OCR", "Document OCR"),
    ("Fact", "Fact Checker"),
    ("Settings", "Settings / About"),
    ("FAQ", "FAQ"),
    ("Privacy", "Privacy Policy"),
]

# Sidebar Navigation for Mobile
with st.sidebar:
    st.markdown('<div class="sidebar-title">LexTransition AI</div>', unsafe_allow_html=True)
    light_mode_enabled = st.toggle(
        "Light mode",
        value=st.session_state.theme_mode == "light",
        help="Switch between light and dark appearance",
    )
    selected_mode = "light" if light_mode_enabled else "dark"
    if selected_mode != st.session_state.theme_mode:
        st.session_state.theme_mode = selected_mode
        st.rerun()

    for page, label in nav_items:
        if st.button(label, key=f"side_{page}", use_container_width=True):
            st.session_state.current_page = page
            st.rerun()
    st.markdown('<div class="sidebar-badge">Offline Mode • V1.0</div>', unsafe_allow_html=True)

header_links = []
for page, label in nav_items:
    page_html = html_lib.escape(page)
    label_html = html_lib.escape(label)
    active_class = "active" if st.session_state.current_page == page else ""
    header_links.append(
        f'<a class="top-nav-link {active_class}" href="?page={page_html}" target="_self" '
        f'title="{label_html}" aria-label="{label_html}">{label_html}</a>'
    )

st.markdown(
    f"""
<a class="site-logo" href="?page=Home" target="_self"><span class="logo-icon">⚖️</span><span class="logo-text">LexTransition AI</span></a>

<div class="top-header">
  <div class="top-header-inner">
    <div class="top-header-left">
      <a class="top-brand" href="?page=Home" target="_self">LexTransition AI</a>
    </div>
    <div class="top-header-center">
      <div class="top-nav">{''.join(header_links)}</div>
      <a class="top-cta" href="?page=Fact" target="_self">Get Started</a>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

current_page = st.session_state.current_page

try:

# ============================================================================
# PAGE: IPC TO BNS MAPPER
# ============================================================================
elif current_page == "Mapper":
    st.markdown("## ✓ IPC → BNS Transition Mapper")
    st.markdown("Convert old IPC sections into new BNS equivalents with legal-grade accuracy.")
    st.divider()
    
    # Input Section
    st.markdown('<div class="mapper-wrap">', unsafe_allow_html=True)
    col1, col2 = st.columns([4, 1])
    with col1:
        search_query = st.text_input("Enter IPC Section", placeholder="e.g., 420, 302, 378")
    with col2:
        st.write("#") # Spacer
        search_btn = st.button("🔍 Find BNS Eq.", use_container_width=True)

    # --- STEP 1: Handle Search Logic & State ---
    if search_query and search_btn:
        if ENGINES_AVAILABLE:
            with st.spinner("Searching database..."):
                res = map_ipc_to_bns(search_query.strip())
                if res:
                    st.session_state['last_result'] = res
                    st.session_state['last_query'] = search_query.strip()
                    # Reset analysis view for new search
                    st.session_state['active_analysis'] = None 
                    st.session_state['active_view_text'] = False
                else:
                    st.session_state['last_result'] = None
                    st.error(f"❌ Section IPC {search_query} not found in database.")
        else:
            st.error("❌ Engines are offline. Cannot perform database lookup.")

        st.markdown('<div class="home-what">What do you want to do?</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.markdown("""
            <a class="home-card" href="?page=Mapper" target="_self">
                <div class="home-card-header">
                    <span class="home-card-icon">✓</span>
                    <div class="home-card-title">Convert IPC to BNS</div>
                </div>
                <div class="home-card-desc">Map old IPC sections to new BNS equivalents.</div>
                <div class="home-card-btn"><span>Open Mapper</span><span>›</span></div>
            </a>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <a class="home-card" href="?page=OCR" target="_self">
                <div class="home-card-header">
                    <span class="home-card-icon">📄</span>
                    <div class="home-card-title">Analyze FIR / Notice</div>
                </div>
            </div>
            <ul class="result-list"><li>{html_lib.escape(notes)}</li></ul>
            <div style="font-size:12px;opacity:0.8;margin-top:10px;">Source: {html_lib.escape(source)}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("###") 

        # --- STEP 3: Action Buttons ---
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            if st.button("🤖 Analyze Differences (AI)", use_container_width=True):
                st.session_state['active_analysis'] = ipc
                st.session_state['active_view_text'] = False

        with col_b:
            if st.button("📄 View Raw Text", use_container_width=True):
                st.session_state['active_view_text'] = True
                st.session_state['active_analysis'] = None

        with col_c:
            if st.button("📝 Summarize Note", use_container_width=True):
                st.session_state['active_analysis'] = None
                st.session_state['active_view_text'] = False
                summary = llm_summarize(notes, question=f"Changes in {ipc}?")
                if summary: 
                    st.success(f"Summary: {summary}")

                    # --- TTS INTEGRATION START (Summary) ---
                    with st.spinner("🎙️ Agent is preparing audio..."):
                        audio_path = tts_engine.generate_audio(summary, "temp_summary.wav")
                        if audio_path and os.path.exists(audio_path):
                            # Replace st.audio with your new custom UI function
                            render_agent_audio(audio_path, title="Legal Summary Dictation")
                    # --- TTS INTEGRATION END ---

                else:
                    st.error("❌ LLM Engine failed to generate summary.")

        # --- STEP 4: Persistent Views (Rendered outside the columns) ---
        
        # 1. AI Analysis View
        if st.session_state.get('active_analysis') == ipc:
            st.divider()
            with st.spinner("Talking to Ollama (AI)..."):
                comp_result = compare_ipc_bns(ipc)
                analysis_text = comp_result.get('analysis', "")
                
                # Check for tag defined in comparator.py
                if "ERROR:" in analysis_text or "Error" in analysis_text or "Connection Error" in analysis_text:
                    st.error(f"❌ AI Error: {analysis_text.replace('ERROR:', '')}")
                    st.info("💡 Make sure Ollama is running (`ollama serve`) and you have pulled the model (`ollama pull llama3`).")
                else:
                    # Final 3-column analysis layout
                    c1, c2, c3 = st.columns([1, 1.2, 1])
                    with c1:
                        st.markdown(f"**📜 IPC {ipc} Text**")
                        st.info(comp_result.get('ipc_text', 'No text available.'))
                    with c2:
                        st.markdown("**🤖 AI Comparison**")
                        st.success(analysis_text)

                    with c3:
                        st.markdown(f"**⚖️ {bns} Text**")
                        st.warning(comp_result.get('bns_text', 'No text available.'))

                    with c2:
                        # --- TTS INTEGRATION START (AI Analysis) ---
                        with st.spinner("🎙️ Agent is analyzing text for dictation..."):
                            audio_path = tts_engine.generate_audio(analysis_text, "temp_analysis.wav")
                            if audio_path and os.path.exists(audio_path):
                                # Replace st.audio with your new custom UI function
                                render_agent_audio(audio_path, title="AI Transition Analysis")
                        # --- TTS INTEGRATION END ---

        # 2. Raw Text View
        elif st.session_state.get('active_view_text'):
            st.divider()
            v1, v2 = st.columns(2)
            with v1:
                st.markdown("**IPC Original Text**")
                st.text_area("ipc_raw", result.get('ipc_full_text', 'No text found in DB'), height=250, disabled=True)
            with v2:
                st.markdown("**BNS Updated Text**")
                st.text_area("bns_raw", result.get('bns_full_text', 'No text found in DB'), height=250, disabled=True)

    # Add Mapping Form (for when sections aren't found)
    with st.expander("➕ Add New Mapping to Database"):
        n_ipc = st.text_input("New IPC Section", value=search_query)
        n_bns = st.text_input("New BNS Section")
        n_ipc_text = st.text_area("IPC Legal Text")
        n_bns_text = st.text_area("BNS Legal Text")
        n_notes = st.text_input("Short Summary/Note")
        
        if st.button("Save to Database"):
            if not n_ipc or not n_bns:
                st.warning("⚠️ IPC and BNS section numbers are required.")
            else:
                success = add_mapping(n_ipc, n_bns, n_ipc_text, n_bns_text, n_notes)
                if success:
                    st.success(f"✅ IPC {n_ipc} successfully mapped to {n_bns} and saved.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Database Error: Failed to save mapping. Is the database file locked or missing?")

        st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# PAGE: DOCUMENT OCR
# ============================================================================
elif current_page == "OCR":
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
                        if audio_path and os.path.exists(audio_path):
                            render_agent_audio(audio_path, title="Action Items Dictation")
                    # --- TTS INTEGRATION END ---

                else:
                    st.warning("⚠ No action items found.")

            except Exception as e:
                st.error("🚨 Something went wrong during OCR processing.")
                st.exception(e)

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
                    else:
                        st.warning("⚠ No action items found.")

                except Exception as e:
                    st.error("🚨 Something went wrong during OCR processing.")
                    st.exception(e)

    # ============================================================================
    # PAGE: FACT CHECKER
    # ============================================================================
    elif current_page == "Fact":

        st.markdown("## 📚 Grounded Fact Checker")
        st.markdown("Ask a legal question to verify answers with citations from official PDFs.")
        st.divider()

        col1, col2 = st.columns([2, 1])

            if res:
                st.success("✅ Verification complete!")
                st.markdown(res)
                
                # --- TTS INTEGRATION START (Fact Checker) ---
                with st.spinner("🎙️ Agent is preparing the verbal citation..."):
                    # Pass the 'res' string directly to the audio engine
                    audio_path = tts_engine.generate_audio(res, "temp_fact_check.wav")
                    if audio_path and os.path.exists(audio_path):
                        render_agent_audio(audio_path, title="Legal Fact Dictation")
                # --- TTS INTEGRATION END ---
                
            else:
                st.info("⚠ No citations found for this query.")

        with col2:
            verify_btn = st.button("📖 Verify", use_container_width=True)

        if verify_btn:

            if not user_question or not user_question.strip():
                st.warning("⚠ Please enter a question first.")
                st.stop()

            if not ENGINES_AVAILABLE:
                st.error("❌ RAG Engine offline.")
                st.stop()

            try:
                # Dummy call logic could go here
                st.success("AI System Online")
            except Exception:
                st.error("AI System Offline")

# ============================================================================
# PAGE: PRIVACY POLICY
# ============================================================================
elif current_page == "Privacy":
    st.markdown("## 🔒 Privacy Policy")
    st.markdown("**Last updated:** February 2025")
    st.divider()
    st.markdown("""
LexTransition AI is designed with **privacy first**. This policy explains how we handle your data when you use this application.

### Data We Process

- **Offline-first:** The application can run entirely on your machine. No legal documents, section queries, or uploaded files are sent to external servers by default.
- **Uploaded files:** Documents you upload (FIRs, notices, PDFs) are processed locally. They may be stored temporarily in project folders (e.g. `law_pdfs/`) on the machine where the app runs.
- **Mapping data:** IPC→BNS mapping lookups use the local database (`mapping_db.json`) and do not leave your environment.
- **OCR & AI:** When using local OCR (EasyOCR/pytesseract) and a local LLM (e.g. Ollama), all processing stays on your device.

### Optional External Services

- If you deploy the app (e.g. Streamlit Cloud), the hosting provider’s terms and data policies apply to that deployment.
- Icons or assets loaded from CDNs (e.g. Flaticon, Simple Icons) are subject to those services’ privacy policies.

### Your Rights

You control the data on your instance. You can delete uploaded PDFs and local mapping data at any time. For hosted deployments, refer to the host’s data retention and deletion policies.

### Changes

We may update this policy from time to time. The “Last updated” date at the top reflects the latest revision. Continued use of the app after changes constitutes acceptance of the updated policy.

### Contact

For questions about this Privacy Policy or LexTransition AI, please open an issue or discussion on the project’s GitHub repository.
""")


# ============================================================================
# PAGE: FAQ
# ============================================================================
elif current_page == "FAQ":
    st.markdown("## ❓ Frequently Asked Questions")
    st.markdown("Quick answers to common questions about LexTransition AI.")
    st.divider()

    with st.expander("**What is LexTransition AI?**"):
        st.markdown("""
LexTransition AI is an **offline-first legal assistant** that helps you navigate the transition from old Indian laws (IPC, CrPC, IEA) to the new BNS, BNSS, and BSA frameworks. It offers:
- **IPC → BNS Mapper:** Convert old section numbers to new equivalents with notes.
- **Document OCR:** Extract text from FIRs and legal notices; get action items in plain language.
- **Grounded Fact Checker:** Ask legal questions and get answers backed by citations from your uploaded law PDFs.
""")

    with st.expander("**Does my data leave my computer?**"):
        st.markdown("""
When run locally with default settings, **no**. Documents, section queries, and uploads are processed on your machine. Local OCR and local LLM (e.g. Ollama) keep everything offline. If you use a hosted version (e.g. Streamlit Cloud), that provider’s infrastructure and policies apply.
""")

    with st.expander("**How do I find the BNS equivalent of an IPC section?**"):
        st.markdown("""
Go to **IPC → BNS Mapper**, enter the IPC section number (e.g. 420, 302, 378), and click **Find BNS Eq.** The app looks up the mapping in the local database and shows the corresponding BNS section and notes. You can also use **Analyze Differences (AI)** if you have Ollama running for a plain-language comparison.
""")

    with st.expander("**Can I add my own IPC–BNS mappings?**"):
        st.markdown("""
Yes. On the Mapper page, use the **Add New Mapping to Database** expander. Enter IPC section, BNS section, optional legal text for both, and a short note. Click **Save to Database** to persist the mapping for future lookups.
""")

    with st.expander("**How does the Fact Checker work?**"):
        st.markdown("""
The Fact Checker uses the PDFs you upload (or place in `law_pdfs/`). You ask a question; the app searches those documents and returns answers with citations. For better results, use official law PDFs and ensure they are indexed (upload via the app or add files to the folder and reload).
""")

    with st.expander("**What file types can I upload for OCR?**"):
        st.markdown("""
The Document OCR page accepts **images** (JPG, PNG, JPEG) of legal notices or FIRs. Upload a file, then click **Extract & Analyze** to get extracted text and, if available, an AI-generated summary of action items (when a local LLM is configured).
""")

    with st.expander("**The app says \"Engines are offline.\" What should I do?**"):
        st.markdown("""
This usually means required components (mapping DB, OCR, or RAG) failed to load. Check that dependencies are installed (`pip install -r requirements.txt`), that `mapping_db.json` exists, and that Tesseract/EasyOCR is available if you use OCR. For AI features, ensure Ollama (or your LLM) is running and reachable.
""")

    with st.expander("**Where is the mapping data stored?**"):
        st.markdown("""
Mappings are stored in **`mapping_db.json`** in the project root. You can edit this file or use the Mapper UI to add/update entries. For bulk updates, use the engine’s import/export utilities (e.g. CSV/Excel) if available in your build.
""")

# Footer
st.markdown(
    """
<div class="app-footer">
  <div class="app-footer-inner">
    <span class="top-chip">Offline Mode</span>
    <span class="top-chip">Privacy First</span>
    <a class="top-credit" href="?page=Privacy" target="_self">Privacy Policy</a>
    <a class="top-credit" href="?page=FAQ" target="_self">FAQ</a>
    <a class="top-credit" href="https://www.flaticon.com/" target="_blank" rel="noopener noreferrer">Icons: Flaticon</a>
    <div class="footer-socials">
      <a href="https://github.com/SharanyaAchanta/" target="_blank" rel="noopener noreferrer" class="footer-social-icon" title="GitHub">
        <img src="https://cdn.simpleicons.org/github/ffffff" height="20" alt="GitHub">
      </a>
      <a href="https://share.streamlit.io/user/sharanyaachanta" target="_blank" rel="noopener noreferrer" class="footer-social-icon" title="Streamlit">
        <img src="https://cdn.simpleicons.org/streamlit/ff4b4b" height="20" alt="Streamlit">
      </a>
      <a href="https://linkedin.com/in/sharanya-achanta-946297276" target="_blank" rel="noopener noreferrer" class="footer-social-icon" title="LinkedIn">
        <img src="https://upload.wikimedia.org/wikipedia/commons/8/81/LinkedIn_icon.svg" height="20" alt="LinkedIn">
      </a>
    </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

except Exception as e:
    st.error("Unexpected Error")
    st.exception(e)
