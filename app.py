import streamlit as st
# Trigger reload for CSS update (Nav 2-line + Button Fix)
import os
import html as html_lib
import re
import time
import base64
# Import TTS engine 
from engine.tts_handler import tts_engine
from engine.github_stats import get_github_stats

# ===== READ THEME FROM URL =====
query_theme = st.query_params.get("theme")

if "theme" not in st.session_state:
    if query_theme:
        st.session_state.theme = query_theme
    else:
        st.session_state.theme = "dark"

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

# ================= THEME SYSTEM =================
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
    
def toggle_theme():
    new_theme = "light" if st.session_state.theme == "dark" else "dark"
    st.session_state.theme = new_theme
    
    # save in URL (IMPORTANT)
    st.query_params["theme"] = new_theme

# toggle button
col1, col2 = st.columns([10,1])
with col2:
    icon = "🌙" if st.session_state.theme == "dark" else "☀️"
    if st.button(icon):
        toggle_theme()
        st.rerun()


# APPLY THEME FIRST (VERY IMPORTANT)
if st.session_state.theme == "light":
    st.markdown("""
    <style>

    html, body, .stApp {
        background:#f8fafc !important;
    }

    [data-testid="stAppViewContainer"]{
        background:#f8fafc !important;
    }

    /* TEXT */
    h1,h2,h3,h4,h5,h6,p,span,label,div{
        color:#0f172a !important;
    }

    /* HEADER */
    .top-header{
        background:#ffffff!important;
        border:1px solid rgba(0,0,0,0.08)!important;
    }

    .top-brand,.top-nav-link{
        color:#0f172a!important;
    }

    /* HOME CARDS */
    .home-card{
        background:#ffffff !important;
        border:1px solid rgba(0,0,0,0.08)!important;
        box-shadow:0 4px 12px rgba(0,0,0,0.08)!important;
    }

    .home-card-title{color:#0f172a!important;}
    .home-card-desc{color:#334155!important;}
    .home-what{color:#0f172a!important;}

    /* OCR UPLOAD BOX */
    [data-testid="stFileUploader"]{
        background:#ffffff !important;
        border:2px dashed #cbd5e1 !important;
        border-radius:12px !important;
        padding:20px !important;
    }

    section[data-testid="stFileUploaderDropzone"]{
        background:#f8fafc !important;
        border:2px dashed #94a3b8 !important;
    }

    section[data-testid="stFileUploaderDropzone"] span{
        color:#0f172a !important;
        font-weight:600;
    }

    /* SIDEBAR */
    [data-testid="stSidebarNav"]{
        background:#ffffff !important;
    }

    /* BUTTON */
    .stButton>button{
        background:#2563eb!important;
        color:white!important;
        border:none!important;
    }

    [data-testid="stFileUploader"] button {
        background:#2563eb !important;
        color:#ffffff !important;
        border:none !important;
        padding:10px 18px !important;
        border-radius:8px !important;
        font-weight:600 !important;
    }
    
    /* hover */
    [data-testid="stFileUploader"] button:hover {
        background:#1d4ed8 !important;
        color:#fff !important;
    }
    
    /* remove black default */
    [data-testid="stFileUploader"] button span{
        color:white !important;
    }

    </style>
    """, unsafe_allow_html=True)

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
    if url_page in {"Home", "Mapper", "OCR", "Fact", "Community", "Settings", "Privacy", "FAQ"}:
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
    current_theme = st.session_state.get("theme", "dark")

    header_links.append(
         f'<a class="top-nav-link {active_class}" href="?page={page_html}&theme={current_theme}" target="_self" '
         f'title="{label_html}" aria-label="{label_html}">{label_html}</a>'
    ) 

st.markdown(
    f"""
<a class="site-logo" href="?page=Home&theme={st.session_state.theme}" target="_self"><span class="logo-icon">⚖️</span><span class="logo-text">LexTransition AI</span></a>

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
    if current_page == "Home":
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
                <div class="home-card-desc">Extract text and action items from FIRs and notices.</div>
                <div class="home-card-btn"><span>Open OCR</span><span>›</span></div>
            </a>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col3, col4 = st.columns(2, gap="large")
        with col3:
            st.markdown(f"""
            <a class="home-card" href="?page=Fact&theme={st.session_state.theme}" target="_self">
                <div class="home-card-header">
                    <span class="home-card-icon">📚</span>
                    <div class="home-card-title">Legal Research</div>
                </div>
                <div class="home-card-desc">Search and analyze case law and statutes.</div>
                <div class="home-card-btn"><span>Start Research</span><span>›</span></div>
            </a>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <a class="home-card" href="?page=Settings&theme={st.session_state.theme}" target="_self">
                <div class="home-card-header">
                    <span class="home-card-icon">⚙️</span>
                    <div class="home-card-title">Settings</div>
                </div>
                <div class="home-card-desc">Configure engines and offline settings.</div>
                <div class="home-card-btn"><span>Configure</span><span>›</span></div>
            </a>
            """, unsafe_allow_html=True)
        
        st.divider()
        st.markdown("""
        ### Why LexTransition AI?
        - **100% Offline:** All processing, including AI summaries and OCR, stays on your machine.
        - **Legal Accuracy:** Mappings are sourced from official government gazettes.
        - **Grounded Responses:** The Fact-Checker cites exact pages from official Law PDFs.
        """)

    elif current_page == "Mapper":
        st.markdown("## 🔄 IPC → BNS Transition Mapper")
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

        # Handle Search Logic
        if search_query and search_btn:
            if ENGINES_AVAILABLE:
                with st.spinner("Searching database..."):
                    res = map_ipc_to_bns(search_query.strip())
                    if res:
                        st.session_state['last_result'] = res
                        st.session_state['last_query'] = search_query.strip()
                        st.session_state['active_analysis'] = None 
                        st.session_state['active_view_text'] = False
                    else:
                        st.session_state['last_result'] = None
                        st.error(f"❌ Section IPC {search_query} not found in database.")
            else:
                st.error("❌ Engines are offline. Cannot perform database lookup.")

        # Display Result
        if st.session_state.get('last_result'):
            result = st.session_state['last_result']
            ipc = st.session_state.get('last_query', "Unknown")
            bns = result.get('bns_section', 'N/A')
            notes = result.get('notes', 'No notes available.')
            source = result.get('source', 'Official Gazette')

            st.markdown(f"""
            <div class="result-card">
                <div class="result-header">
                    <span class="result-badge">Section Transition</span>
                    <h3 style="margin:0;color:#f8fafc;">IPC {ipc} → {bns}</h3>
                </div>
                <div class="result-body" style="margin-top:15px;">
                    <ul class="result-list">
                        <li style="color:#cbd5e1;list-style:none;">{html_lib.escape(notes)}</li>
                    </ul>
                    <div style="font-size:12px;opacity:0.8;margin-top:10px;color:#94a3b8;">Source: {html_lib.escape(source)}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("###") 
            # Action Buttons
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
                        st.info(f"**AI Summary:** {summary}")
                        with st.spinner("🎙️ Agent is preparing audio..."):
                            audio_path = tts_engine.generate_audio(summary, "temp_summary.wav")
                            if audio_path and os.path.exists(audio_path):
                                render_agent_audio(audio_path, title="Legal Summary Dictation")
                    else:
                        st.error("❌ LLM Engine failed to generate summary.")

            # Persistent Views
            if st.session_state.get('active_analysis') == ipc:
                st.divider()
                with st.spinner("Analyzing with AI..."):
                    comp_result = compare_ipc_bns(ipc)
                    analysis_text = comp_result.get('analysis', "")
                    if "ERROR:" in analysis_text:
                        st.error(f"❌ AI Error: {analysis_text}")
                    else:
                        c1, c2, c3 = st.columns([1, 1.2, 1])
                        with c1:
                            st.markdown(f"**📜 IPC {ipc} Text**")
                            st.info(comp_result.get('ipc_text', 'No text available.'))
                        with c2:
                            st.markdown("**🤖 AI Comparison**")
                            st.success(analysis_text)
                            with st.spinner("🎙️ Preparing dictation..."):
                                audio_path = tts_engine.generate_audio(analysis_text, "temp_analysis.wav")
                                if audio_path and os.path.exists(audio_path):
                                    render_agent_audio(audio_path, title="AI Transition Analysis")
                        with c3:
                            st.markdown(f"**⚖️ {bns} Text**")
                            st.warning(comp_result.get('bns_text', 'No text available.'))

            elif st.session_state.get('active_view_text'):
                st.divider()
                v1, v2 = st.columns(2)
                with v1:
                    st.markdown("**IPC Original Text**")
                    st.text_area("ipc_raw", result.get('ipc_full_text', 'No text found in DB'), height=250, disabled=True)
                with v2:
                    st.markdown("**BNS Updated Text**")
                    st.text_area("bns_raw", result.get('bns_full_text', 'No text found in DB'), height=250, disabled=True)

        # Add Mapping Form
        with st.expander("➕ Add New Mapping to Database"):
            n_ipc = st.text_input("New IPC Section")
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
                        st.success(f"✅ IPC {n_ipc} mapped to {n_bns} successfully.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Failed to save mapping.")

    elif current_page == "OCR":
        st.markdown("## 🖼️ Document OCR")
        st.markdown("Extract text and key action items from legal notices, FIRs, and scanned documents.")
        st.divider()
        
        col1, col2 = st.columns([1, 1])
        with col1:
            uploaded_file = st.file_uploader("Upload (FIR/Notice)", type=["jpg", "png", "jpeg"])
            if uploaded_file:
                st.image(uploaded_file, caption="Uploaded Document", use_container_width=True)
        
        with col2:
            if st.button("🔧 Extract & Analyze", use_container_width=True):
                if uploaded_file:
                    if ENGINES_AVAILABLE:
                        try:
                            with st.spinner("🔍 Processing OCR..."):
                                raw = uploaded_file.getvalue()
                                extracted = extract_text(raw)
                            
                            if extracted and extracted.strip():
                                st.success("✅ Text extraction completed!")
                                st.text_area("Extracted Text", extracted, height=300)
                                
                                with st.spinner("🤖 Analyzing action items..."):
                                    summary = llm_summarize(extracted, question="What are the action items?")
                                if summary:
                                    st.info(f"**AI Analysis:** {summary}")
                                    with st.spinner("🎙️ Preparing audio..."):
                                        audio_path = tts_engine.generate_audio(summary, "temp_ocr.wav")
                                        if audio_path and os.path.exists(audio_path):
                                            render_agent_audio(audio_path, title="Action Items Dictation")
                                else:
                                    st.warning("⚠ Could not generate action items.")
                            else:
                                st.warning("⚠ No text detected.")
                        except Exception as e:
                            st.error(f"🚨 OCR Error: {e}")
                    else:
                        st.error("❌ OCR Engine not available.")
                else:
                    st.warning("⚠ Please upload a file first.")

    elif current_page == "Fact":
        st.markdown("## 📚 Grounded Fact Checker")
        st.markdown("Ask a legal question to verify answers with citations from official PDFs.")
        st.divider()

        user_question = st.text_input("Ask a legal question...", placeholder="e.g., What is the punishment for murder?")
        
        if st.button("📖 Verify", use_container_width=True):
            if user_question:
                if ENGINES_AVAILABLE:
                    with st.spinner("Searching official Law PDFs..."):
                        res = search_pdfs(user_question)
                        if res:
                            st.success("✅ Verification complete!")
                            st.markdown(res)
                            with st.spinner("🎙️ Preparing audio..."):
                                audio_path = tts_engine.generate_audio(res, "temp_fact.wav")
                                if audio_path and os.path.exists(audio_path):
                                    render_agent_audio(audio_path, title="Legal Fact Dictation")
                        else:
                            st.info("⚠ No exact citations found. Try a different query.")
                else:
                    st.error("❌ RAG Engine offline.")
            else:
                st.warning("⚠ Please enter a question.")

    elif current_page == "Settings":
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

    elif current_page == "FAQ":
        st.markdown("## ❓ Frequently Asked Questions")
        st.divider()
        with st.expander("**What is LexTransition AI?**"):
            st.write("An offline-first legal assistant for IPC to BNS transition.")
        with st.expander("**Is my data safe?**"):
            st.write("Yes, all processing is local. No data is sent to the cloud.")

    elif current_page == "Privacy":
        st.markdown("## 🔒 Privacy Policy")
        st.divider()
        st.write("LexTransition AI processes all data locally on your device. We do not collect or store your personal information on any external servers.")

    elif current_page == "Community":
        st.markdown("## 🤝 Community Hub")
        st.markdown("Join us in building the future of offline legal technology in India.")
        st.divider()
        
        gh_stats = get_github_stats()
        
        # Stats Dashboard
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("⭐ Stars", gh_stats.get('stars', 0))
        with c2:
            st.metric("🍴 Forks", gh_stats.get('forks', 0))
        with c3:
            st.metric("🔄 Pull Requests", gh_stats.get('pull_requests', 0))
        with c4:
            st.metric("🐞 Open Issues", gh_stats.get('issues', 0))
            
        st.write("###")
        
        col_main, col_side = st.columns([2, 1])
        
        with col_main:
            st.markdown("""
            ### 🚀 How to Contribute
            Whether you are a developer, a legal professional, or a student, your help is invaluable!
            
            - **Report Bugs**: Found an edge case in transition mapping? Let us know.
            - **Improve Mappings**: Help us verify more sections between IPC and BNS.
            - **Code**: Check out our 'Good First Issues' on GitHub.
            - **Documentation**: Help us make the legal explanations clearer for everyone.
            """)
            
            st.markdown(f"""
            <a href="https://github.com/SharanyaAchanta/LexTransition-AI" target="_blank" style="text-decoration:none;">
                <div style="background:rgba(203, 166, 99, 0.1); border:1px solid rgba(203, 166, 99, 0.4); padding:20px; border-radius:10px; text-align:center;">
                    <h3 style="color:#cb924f; margin:0;">View on GitHub</h3>
                    <p style="color:#94a3b8; margin:10px 0 0;">Browse the source code, issues, and discussions.</p>
                </div>
            </a>
            """, unsafe_allow_html=True)
            
        with col_side:
            st.markdown("""
            ### 📜 Project Info
            - **License**: MIT
            - **Stack**: Python, Streamlit, Ollama
            - **Goal**: Privacy-first legal awareness.
            """)
            st.info("💡 **Tip**: Mention this project on LinkedIn to help more legal professionals transition to the new laws!")

    # Fetch GitHub Stats
    gh_stats = get_github_stats()

    # Footer with dynamic GitHub stats & Community Link
    # Note: Removed blank lines and internal comments to fix markdown parsing issues
    st.markdown(
        f"""
<div class="app-footer">
<div class="app-footer-inner" style="flex-direction: column; align-items: flex-start; gap: 12px;">
<div style="display: flex; align-items: center; gap: 15px; width: 100%; flex-wrap: wrap;">
<span class="top-chip">Offline Mode</span>
<span class="top-chip">Privacy First</span>
<a class="top-credit" href="?page=Privacy" target="_self">Privacy Policy</a>
<a class="top-credit" href="?page=FAQ" target="_self">FAQ</a>
</div>
<div style="display: flex; align-items: center; justify-content: space-between; width: 100%; flex-wrap: wrap; gap: 12px;">
<div class="footer-stats" style="display:flex; gap:10px; align-items: center;">
<div class="stat-item" title="Stars" style="display:flex; align-items:center; gap:5px; background:rgba(255,255,255,0.05); padding:4px 10px; border-radius:15px; border:1px solid rgba(255,255,255,0.1); color:#e2e8f0; font-size:12px; font-weight:600;">
<span style="color:#eab308;">⭐</span> {gh_stats.get('stars', 0)}
</div>
<div class="stat-item" title="Forks" style="display:flex; align-items:center; gap:5px; background:rgba(255,255,255,0.05); padding:4px 10px; border-radius:15px; border:1px solid rgba(255,255,255,0.1); color:#e2e8f0; font-size:12px; font-weight:600;">
<span style="color:#94a3b8;">🍴</span> {gh_stats.get('forks', 0)}
</div>
<div class="stat-item" title="Pull Requests" style="display:flex; align-items:center; gap:5px; background:rgba(255,255,255,0.05); padding:4px 10px; border-radius:15px; border:1px solid rgba(255,255,255,0.1); color:#e2e8f0; font-size:12px; font-weight:600;">
<span style="color:#60a5fa;">🔄</span> {gh_stats.get('pull_requests', 0)}
</div>
<div class="stat-item" title="Open Issues" style="display:flex; align-items:center; gap:5px; background:rgba(255,255,255,0.05); padding:4px 10px; border-radius:15px; border:1px solid rgba(255,255,255,0.1); color:#e2e8f0; font-size:12px; font-weight:600;">
<span style="color:#f87171;">🐞</span> {gh_stats.get('issues', 0)}
</div>
</div>
<div class="footer-socials" style="display:flex; gap:12px; align-items:center;">
<a href="?page=Community" target="_self" class="footer-social-link" title="Community Hub" style="display:flex; align-items:center; text-decoration:none; background:rgba(255, 255, 255, 0.05); border:1px solid rgba(255, 255, 255, 0.1); padding:6px; border-radius:6px; transition: all 0.2s ease;">
<span style="font-size:18px;">🤝</span>
</a>
<a href="https://github.com/SharanyaAchanta/LexTransition-AI" target="_blank" title="View Source on GitHub" style="display:flex; align-items:center; text-decoration:none; background:rgba(255, 255, 255, 0.05); border:1px solid rgba(255, 255, 255, 0.1); padding:6px; border-radius:6px; transition: all 0.2s ease;">
<img src="https://cdn.simpleicons.org/github/ffffff" height="18" alt="GitHub">
</a>
<a href="https://linkedin.com/in/sharanya-achanta-946297276" target="_blank" title="LinkedIn" style="opacity:0.8; transition:opacity 0.2s; display: flex;">
<img src="https://upload.wikimedia.org/wikipedia/commons/8/81/LinkedIn_icon.svg" height="18" alt="LinkedIn">
</a>
</div>
</div>
</div>
</div>
""",
        unsafe_allow_html=True,
    )

except Exception as e:
    st.error("🚨 An unexpected error occurred.")
    st.exception(e)
