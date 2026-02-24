import streamlit as st
# Trigger reload for CSS update (Nav 2-line + Button Fix)
import os
import html as html_lib
import re
import time
import base64

# Import TTS engine 
from engine.tts_handler import tts_engine
from engine.github_stats import get_github_stats, get_github_contributors
from engine.risk_analyzer import analyze_risk
from engine.bail_analyzer import analyze_bail
from engine.summarizer import generate_summary
from engine.deadline_extractor import analyze_deadlines

# Import STT engine
from engine.stt_handler import get_stt_engine
from streamlit_mic_recorder import mic_recorder

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

# Page Configuration
st.set_page_config(page_title="LexTransition AI", page_icon="⚖️", layout="wide")

# Access the CSS file
def load_css(file_path):
    if os.path.exists(file_path):
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load the CSS file
load_css("assets/styles.css")

# Initialize session state for navigation
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# Security helpers (avoid path traversal / HTML injection in UI-rendered HTML)
_SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]+")

def _safe_filename(name: str, default: str) -> str:
    base = os.path.basename(name or "").strip().replace("\x00", "")
    if not base:
        return default
    safe = _SAFE_FILENAME_RE.sub("_", base).strip("._")
    return safe or default

def _dedupe_path(path: str) -> str:
    if not os.path.exists(path):
        return path
    stem, ext = os.path.splitext(path)
    i = 1
    while True:
        candidate = f"{stem}_{i}{ext}"
        if not os.path.exists(candidate):
            return candidate
        i += 1

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

# load css
def load_css(file_path):
    if os.path.exists(file_path):
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# If a sidebar navigation is pending, take precedence over URL param once
if "pending_page" in st.session_state:
    st.session_state.current_page = st.session_state.pop("pending_page")
else:
    if url_page in {"Home", "Mapper", "OCR", "Fact", "Settings"}:
        st.session_state.current_page = url_page

# Helper: navigate via sidebar and keep URL in sync
def _goto(page: str):
    # Defer assignment to top-of-run logic so it overrides URL param this cycle
    st.session_state.pending_page = page
    try:
        st.experimental_set_query_params(page=page)
    except Exception:
        pass
    st.rerun()

# Header Navigation
nav_items = [
    ("Home", "Home"),
    ("Mapper", "IPC -> BNS Mapper"),
    ("OCR", "Document OCR"),
    ("Fact", "Fact Checker"),
    ("Settings", "Settings / About"),
]

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
<!-- Compact fixed site logo -->
<a class="site-logo" href="?page=Home" target="_self"><span class="logo-icon">⚖️</span><span class="logo-text">LexTransition AI</span></a>

<div class="top-header">
  <div class="top-header-inner">
    <div class="top-header-left">
      <!-- header brand is hidden by CSS; left here for semantics/accessibility -->
      <a class="top-brand" href="?page=Home" target="_self">LexTransition AI</a>
    </div>
    <div class="top-header-center">
      <div class="top-nav">{''.join(header_links)}</div>
    </div>
    <div class="top-header-right">
      <a class="top-cta" href="?page=Fact" target="_self">Get Started</a>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# Attempt to import engines (use stubs if missing)
try:
    from engine.ocr_processor import extract_text, available_engines
    from engine.mapping_logic import map_ipc_to_bns, add_mapping
    from engine.rag_engine import search_pdfs, add_pdf, index_pdfs
    from engine.llm import summarize as llm_summarize
    ENGINES_AVAILABLE = True
except Exception:
    ENGINES_AVAILABLE = False

# LLM summarize stub
try:
    from engine.llm import summarize as llm_summarize
except Exception:
    def llm_summarize(text, question=None):
        return None

# Index PDFs at startup if engine available
if ENGINES_AVAILABLE and not st.session_state.get("pdf_indexed"):
    try:
        index_pdfs("law_pdfs")
        st.session_state.pdf_indexed = True
    except Exception:
        pass

# Get current page
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
    
    # Import Glossary Engine
    from engine import glossary as glossary_engine

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
        val = qp.get("page", None)
        if isinstance(val, list):
            return val[0]
        return val
    except Exception:
        return None


url_page = _read_url_page()

if "pending_page" in st.session_state:
    st.session_state.current_page = st.session_state.pop("pending_page")
else:
    if url_page in {"Home", "Mapper", "OCR", "Glossary", "Fact", "Community", "Settings", "Privacy", "FAQ"}:
        st.session_state.current_page = url_page

nav_items = [
    ("Home", "Home"),
    ("Mapper", "IPC -> BNS Mapper"),
    ("OCR", "Document OCR"),
    ("Glossary", "Legal Glossary"),
    ("Fact", "Fact Checker"),
    ("Community", "Community Hub"),
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
    # ============================================================================
    # PAGE: HOME
    # ============================================================================
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

    # ============================================================================
    # PAGE: IPC TO BNS MAPPER
    # ============================================================================
    elif current_page == "Mapper":
        st.markdown("## ✓ IPC → BNS Transition Mapper")
        st.markdown("Convert old IPC sections into new BNS equivalents with legal-grade accuracy.")
        st.divider()
        
        # Input Section Wrapper
        st.markdown('<div class="mapper-wrap">', unsafe_allow_html=True)
        
        # --- 3-column layout: Input | Mic | Search ---
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            # We bind the value to our session state so Voice Input auto-fills this box
            search_query = st.text_input(
                "Search", # A label is required, but we hide it below
                value=st.session_state.get('mapper_search_val', ''),
                placeholder="e.g., 420, 302, 378",
                label_visibility="collapsed" # Aligns perfectly with the buttons
            )
            
        with col2:
            # --- STT Integration Widget ---
            audio_dict = mic_recorder(
                start_prompt="🎙️ Speak",
                stop_prompt="🛑 Stop",
                key='mapper_mic',
                use_container_width=True
            )

        with col3:
            search_btn = st.button("🔍 Find BNS Eq.", use_container_width=True)

        # --- Process Audio ---
        audio_val = audio_dict['bytes'] if audio_dict else None
        
        # Process the audio only once
        if audio_val and audio_val != st.session_state.get("last_audio_mapper"):
            st.session_state["last_audio_mapper"] = audio_val 
            
            temp_path = "temp_audio/mapper_audio.wav"
            os.makedirs("temp_audio", exist_ok=True)
            with open(temp_path, "wb") as f:
                f.write(audio_val)
                
            with st.spinner("🎙️ Agent is listening..."):
                stt_engine = get_stt_engine() 
                text = stt_engine.transcribe_audio(temp_path)
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
                # Whisper will transcribe "Section four twenty" as "Section 420".
                # We use regex to extract just the alphanumeric section (e.g., "420", "498A")
                nums = re.findall(r'\d+[a-zA-Z]?', text) 
                voice_query = nums[0].upper() if nums else text.strip()
                    
                # Update state and trigger an automatic search
                st.session_state['mapper_search_val'] = voice_query
                st.session_state['auto_search'] = True 
                st.rerun()

        # --- Auto-Search from Voice ---
        if st.session_state.get('auto_search'):
            search_btn = True # Spoof the button click
            st.session_state['auto_search'] = False # Instantly reset the flag

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

        st.divider()
        
        # --- STEP 2: Render Persistent Results ---
        # We check session_state instead of search_btn so results survive refreshes
        if st.session_state.get('last_result'):
            result = st.session_state['last_result']
            ipc = st.session_state['last_query']
            bns = result.get("bns_section", "N/A")
            notes = result.get("notes", "See source mapping.")
            source = result.get("source", "mapping_db")
            
            # Render Result Card
            st.markdown(f"""
            <div class="result-card">
                <div class="result-badge">Mapping • found</div>
                <div class="result-grid">
                    <div class="result-col">
                        <div class="result-col-title">IPC Section</div>
                        <div style="font-size:20px;font-weight:700;color:var(--text-color);margin-top:6px;">{html_lib.escape(ipc)}</div>
                    </div>
                    <div class="result-col">
                        <div class="result-col-title">BNS Section</div>
                        <div style="font-size:20px;font-weight:700;color:var(--primary-color);margin-top:6px;">{html_lib.escape(bns)}</div>
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

    # ============================================================================
    # PAGE: LEGAL GLOSSARY
    # ============================================================================
    elif current_page == "Glossary":
        st.markdown("## 📖 Legal Glossary")
        st.markdown("Understand complex legal terms, Latin maxims, and procedural terminology used in Indian Law.")
        st.divider()

        # Search and Filtering
        col1, col2 = st.columns([3, 1])
        with col1:
            g_search = st.text_input("Search terms...", placeholder="e.g., Habeas Corpus, Mens Rea, Evidence")
        with col2:
            categories = ["All"] + glossary_engine.get_categories()
            g_cat = st.selectbox("Category", categories)

        # Alphabet filtering
        st.write("Browse by Letter:")
        letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        cols = st.columns(len(letters))
        selected_letter = None
        for i, l in enumerate(letters):
            if cols[i].button(l, key=f"letter_{l}", use_container_width=True):
                selected_letter = l

        # Results logic
        if g_search:
            results = glossary_engine.search_terms(g_search)
            st.markdown(f"**Found {len(results)} results for \"{g_search}\"**")
        elif selected_letter:
            results = glossary_engine.get_terms_by_letter(selected_letter)
            st.markdown(f"**Terms starting with \"{selected_letter}\"**")
        elif g_cat != "All":
            results = glossary_engine.get_terms_by_category(g_cat)
            st.markdown(f"**Category: {g_cat}**")
        else:
            results = glossary_engine.get_all_terms(limit=20)
            st.markdown("**Recent/Common Terms**")

        st.write("---")

        if not results:
            st.info("No matching terms found. Try searching for something else.")
        else:
            for term in results:
                with st.expander(f"**{term['term']}**"):
                    st.markdown(f"**Definition:** {term['definition']}")
                    if term['related_sections']:
                        st.markdown(f"**Related Sections:** `{term['related_sections']}`")
                    if term['examples']:
                        st.markdown(f"**Example:** *{term['examples']}*")
                    st.caption(f"Category: {term['category']}")
                    
                    if st.button(f"🎙️ Speak Definition", key=f"tts_{term['term']}"):
                        with st.spinner("Preparing audio..."):
                            audio_path = tts_engine.generate_audio(term['definition'], f"temp_term_{term['term']}.wav")
                            if audio_path and os.path.exists(audio_path):
                                render_agent_audio(audio_path, title=f"Term: {term['term']}")

    # ============================================================================
    # PAGE: FACT CHECKER
    # ============================================================================
    elif current_page == "Fact":
        def clean_text_for_tts(text: str) -> str:
            """Removes markdown formatting so the TTS sounds natural."""
            import re
            text = re.sub(r'[*_]{1,3}', '', text)
            text = re.sub(r'>\s?', '', text)
            text = text.replace('\n', ' ')
            return text.strip()
        
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


    # elif current_page == "Settings":
    #     st.markdown("## ⚙️ Settings / About")
    #     st.divider()

        st.divider()
        st.markdown("### 🌟 Project Leadership")
        
        # Responsive CSS for small screens
        st.markdown("""
        <style>
        @media (max-width: 400px) {
            .owner-card { padding: 15px !important; }
            .contributor-card { padding: 15px !important; }
            .stColumns [data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
            }
        }
        </style>
        """, unsafe_allow_html=True)

        contributors = get_github_contributors()
        owner_login = "SharanyaAchanta"
        
        if contributors:
            owner_data = next((c for c in contributors if c['login'] == owner_login), None)
            other_contributors = [c for c in contributors if c['login'] != owner_login]
            
            if owner_data:
                st.markdown(f"""
                <div class="owner-card" style="
                    background: linear-gradient(135deg, rgba(37, 99, 235, 0.1) 0%, rgba(37, 99, 235, 0.05) 100%);
                    border: 2px solid rgba(37, 99, 235, 0.3);
                    border-radius: 12px;
                    padding: 20px;
                    text-align: center;
                    margin: 0 auto 30px auto;
                    position: relative;
                    max-width: 450px;
                ">
                    <div style="position: absolute; top: 10px; right: 10px; background: #2563eb; color: white; padding: 2px 12px; border-radius: 12px; font-size: 0.65em; font-weight: 800; letter-spacing: 0.5px;">OWNER</div>
                    <img src="{owner_data['avatar_url']}" style="width: 80px; height: 80px; border-radius: 50%; margin-bottom: 12px; border: 3px solid #2563eb;">
                    <h3 style="margin: 0; color: #f8fafc; font-size: 1.3em;">{owner_data['login']}</h3>
                    <p style="color: #94a3b8; font-size: 0.85em; margin-bottom: 12px;">Project Visionary</p>
                    <div style="background: rgba(37, 99, 235, 0.15); color: #60a5fa; padding: 4px 12px; border-radius: 20px; font-size: 0.75em; font-weight: 700; display: inline-block; margin-bottom: 15px;">
                        {owner_data['contributions']} Contributions
                    </div>
                    <a href="{owner_data['html_url']}" target="_blank" style="
                        display: block;
                        background: #2563eb;
                        color: white;
                        text-decoration: none;
                        padding: 10px;
                        border-radius: 6px;
                        font-weight: 600;
                        font-size: 0.85em;
                        transition: background 0.2s;
                    ">View Lead Profile</a>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("### 🤝 Community Contributors")
            
            items_per_page = 6
            if 'contrib_page' not in st.session_state:
                st.session_state.contrib_page = 0
            
            total_pages = (len(other_contributors) + items_per_page - 1) // items_per_page
            
            if total_pages > 0:
                start_idx = st.session_state.contrib_page * items_per_page
                end_idx = start_idx + items_per_page
                current_batch = other_contributors[start_idx:end_idx]
                
                cols_per_row = 3
                for i in range(0, len(current_batch), cols_per_row):
                    row_cols = st.columns(cols_per_row)
                    for j in range(cols_per_row):
                        if i + j < len(current_batch):
                            c = current_batch[i + j]
                            with row_cols[j]:
                                st.markdown(f"""
                                <div class="contributor-card" style="
                                    background: rgba(255, 255, 255, 0.05);
                                    border: 1px solid rgba(255, 255, 255, 0.1);
                                    border-radius: 10px;
                                    padding: 15px;
                                    text-align: center;
                                    margin-bottom: 15px;
                                ">
                                    <img src="{c['avatar_url']}" style="width: 60px; height: 60px; border-radius: 50%; margin-bottom: 10px; border: 2px solid rgba(255,255,255,0.1);">
                                    <div style="font-weight: 700; color: #f8fafc; margin-bottom: 4px; font-size: 0.95em;">{c['login']}</div>
                                    <div style="color: #94a3b8; font-size: 0.75em; margin-bottom: 10px;">{c['contributions']} commits</div>
                                    <a href="{c['html_url']}" target="_blank" style="
                                        display: block;
                                        color: #60a5fa;
                                        text-decoration: none;
                                        font-size: 0.8em;
                                        font-weight: 600;
                                    ">Profile →</a>
                                </div>
                                """, unsafe_allow_html=True)
                
                if total_pages > 1:
                    c1, c2, c3 = st.columns([1, 2, 1])
                    with c1:
                        if st.button("←", disabled=st.session_state.contrib_page == 0):
                            st.session_state.contrib_page -= 1
                            st.rerun()
                    with c2:
                        st.markdown(f"<div style='text-align:center; padding-top:10px; font-size:0.8em; opacity:0.6;'>{st.session_state.contrib_page + 1} / {total_pages}</div>", unsafe_allow_html=True)
                    with c3:
                        if st.button("→", disabled=st.session_state.contrib_page >= total_pages - 1):
                            st.session_state.contrib_page += 1
                            st.rerun()
            else:
                st.info("No other contributors found yet.")
        else:
            st.info("Unable to fetch contributor details.")

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

# Footer Bar
st.markdown(
    """
<div class="app-footer">
  <div class="app-footer-inner">
    <span class="top-chip">Offline Mode</span>
    <span class="top-chip">Privacy First</span>
    <a class="top-credit" href="https://www.flaticon.com/" target="_blank">Icons: Flaticon</a>
  </div>
</div>
""",
    unsafe_allow_html=True,
)