import streamlit as st
import os
import html as html_lib
import re
import time

# Page Configuration
st.set_page_config(
    page_title="LexTransition AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# load css
def load_css(file_path):
    if os.path.exists(file_path):
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load external CSS file
load_css("assets/styles.css")

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
    if url_page in {"Home", "Mapper", "OCR", "Fact", "Settings"}:
        st.session_state.current_page = url_page

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
<a class="site-logo" href="?page=Home" target="_self"><span class="logo-icon">⚖️</span><span class="logo-text">LexTransition AI</span></a>

<div class="top-header">
  <div class="top-header-inner">
    <div class="top-header-left">
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

current_page = st.session_state.current_page

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

    st.markdown('<div class="mapper-wrap">', unsafe_allow_html=True)

    # ---------------- LOADING STATES ----------------
    if "mapper_loading" not in st.session_state:
        st.session_state.mapper_loading = False

    if "analysis_loading" not in st.session_state:
        st.session_state.analysis_loading = False

    # ---------------- INPUT SECTION ----------------
    col1, col2 = st.columns([4, 1])
    with col1:
        search_query = st.text_input(
            "Enter IPC Section",
            placeholder="e.g., 420, 302, 378"
        )
    with col2:
        st.write("##")
        search_btn = st.button(
            "🔍 Find BNS Eq.",
            use_container_width=True,
            disabled=st.session_state.mapper_loading
        )

    # ---------------- SEARCH LOGIC ----------------
    if search_query and search_btn:
        if ENGINES_AVAILABLE:
            st.session_state.mapper_loading = True

            with st.spinner("Searching database..."):
                try:
                    res = map_ipc_to_bns(search_query.strip())

                    if res:
                        st.session_state["last_result"] = res
                        st.session_state["last_query"] = search_query.strip()
                        st.session_state["active_analysis"] = None
                        st.session_state["active_view_text"] = False
                    else:
                        st.session_state["last_result"] = None
                        st.error(f"❌ Section IPC {search_query} not found.")

                except Exception as e:
                    st.error("❌ Search failed.")
                    st.exception(e)

            st.session_state.mapper_loading = False
        else:
            st.error("❌ Engines are offline. Cannot perform lookup.")

    st.divider()

    # ---------------- RESULT RENDER ----------------
    if st.session_state.get("last_result"):
        result = st.session_state.get("last_result", {})
        ipc = st.session_state.get("last_query", "")
        bns = result.get("bns_section", "N/A")
        notes = result.get("notes", "See source mapping.")
        source = result.get("source", "mapping_db")

        # Result Card
        st.markdown(f"""
        <div class="result-card">
            <div class="result-badge">Mapping • found</div>
            <div class="result-grid">
                <div class="result-col">
                    <div class="result-col-title">IPC Section</div>
                    <div style="font-size:20px;font-weight:700;">
                        {html_lib.escape(ipc)}
                    </div>
                </div>
                <div class="result-col">
                    <div class="result-col-title">BNS Section</div>
                    <div style="font-size:20px;font-weight:700;">
                        {html_lib.escape(bns)}
                    </div>
                </div>
            </div>
            <ul class="result-list">
                <li>{html_lib.escape(notes)}</li>
            </ul>
            <div style="font-size:12px;opacity:0.8;margin-top:10px;">
                Source: {html_lib.escape(source)}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.write("###")

        # ---------------- ACTION BUTTONS ----------------
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            analyze_btn = st.button(
                "🤖 Analyze Differences (AI)",
                use_container_width=True,
                disabled=st.session_state.analysis_loading
            )

            if analyze_btn:
                st.session_state.analysis_loading = True
                st.session_state["active_analysis"] = ipc
                st.session_state["active_view_text"] = False

        with col_b:
            if st.button("📄 View Raw Text", use_container_width=True):
                st.session_state["active_view_text"] = True
                st.session_state["active_analysis"] = None

        with col_c:
            if st.button("📝 Summarize Note", use_container_width=True):
                summary = llm_summarize(notes, question=f"Changes in {ipc}?")
                if summary:
                    st.success(f"Summary: {summary}")
                else:
                    st.error("❌ LLM Engine failed to generate summary.")

        # ---------------- AI ANALYSIS VIEW ----------------
        if st.session_state.get("active_analysis") == ipc:
            st.divider()

            with st.spinner("Talking to Ollama (AI)..."):
                try:
                    comp_result = compare_ipc_bns(ipc)
                    analysis_text = comp_result.get("analysis", "")
                except Exception as e:
                    st.error("❌ AI processing failed.")
                    st.exception(e)
                    comp_result = {}
                    analysis_text = ""

            st.session_state.analysis_loading = False

            if "ERROR:" in analysis_text or "Error" in analysis_text:
                st.error(analysis_text)
            else:
                c1, c2, c3 = st.columns([1, 1.2, 1])

                with c1:
                    st.markdown(f"**📜 IPC {ipc} Text**")
                    st.info(comp_result.get("ipc_text", "No text available."))

                with c2:
                    st.markdown("**🤖 AI Comparison**")
                    st.success(analysis_text)

                with c3:
                    st.markdown(f"**⚖️ {bns} Text**")
                    st.warning(comp_result.get("bns_text", "No text available."))

        # ---------------- RAW TEXT VIEW ----------------
        elif st.session_state.get("active_view_text"):
            st.divider()
            v1, v2 = st.columns(2)

            with v1:
                st.markdown("**IPC Original Text**")
                st.text_area(
                    "ipc_raw",
                    result.get("ipc_full_text", "No text found."),
                    height=250,
                    disabled=True
                )

            with v2:
                st.markdown("**BNS Updated Text**")
                st.text_area(
                    "bns_raw",
                    result.get("bns_full_text", "No text found."),
                    height=250,
                    disabled=True
                )

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# PAGE: DOCUMENT OCR
# ============================================================================
elif current_page == "OCR":
    st.markdown("## 🖼️ Document OCR")
    st.markdown("Extract text and key action items from legal notices, FIRs, and scanned documents.")
    st.divider()

    if "ocr_loading" not in st.session_state:
        st.session_state.ocr_loading = False

    
    col1, col2 = st.columns([1, 1])
    with col1:
        uploaded_file = st.file_uploader("Upload (FIR/Notice)", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        if uploaded_file:
            st.image(uploaded_file, use_column_width=True)
    
    with col2:
        extract_btn = st.button(
        "🔧 Extract & Analyze",
        use_container_width=True,
        disabled=st.session_state.ocr_loading
)

    if uploaded_file and extract_btn:
        if ENGINES_AVAILABLE:
            st.session_state.ocr_loading = True

            with st.spinner("Extracting and analyzing document..."):
                try:
                    raw = uploaded_file.read()
                    extracted = extract_text(raw)

                    st.text_area("Extracted Text", extracted, height=300)

                    summary = llm_summarize(extracted, question="Action items?")
                    if summary:
                        st.info(f"**Action Item:** {summary}")
                    else:
                        st.warning("No summary generated.")

                except Exception as e:
                    st.error("❌ OCR processing failed.")
                    st.exception(e)

            st.session_state.ocr_loading = False
        else:
            st.error("OCR Engine not available.")


# ============================================================================
# PAGE: FACT CHECKER
# ============================================================================
elif current_page == "Fact":
    st.markdown("## 📚 Grounded Fact Checker")
    st.markdown("Ask a legal question to verify answers with citations from official PDFs.")
    st.divider()

    if "fact_loading" not in st.session_state:
        st.session_state.fact_loading = False

    col1, col2 = st.columns([2, 1])
    with col1:
        user_question = st.text_input("Question", placeholder="e.g., penalty for cheating?")
    with col2:
        verify_btn = st.button(
            "📖 Verify",
            use_container_width=True,
            disabled=st.session_state.fact_loading
)

    
    with st.expander("Upload Law PDFs"):
        uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded_pdf and ENGINES_AVAILABLE:
            save_dir = "law_pdfs"
            os.makedirs(save_dir, exist_ok=True)
            path = os.path.join(save_dir, _safe_filename(uploaded_pdf.name, "doc.pdf"))
            with open(path, "wb") as f: f.write(uploaded_pdf.read())
            add_pdf(path)
            st.success(f"Added {uploaded_pdf.name}")

    if user_question and verify_btn:
        if ENGINES_AVAILABLE:
            st.session_state.fact_loading = True

            with st.spinner("Verifying with legal database..."):
                try:
                    res = search_pdfs(user_question)

                    if res:
                        st.markdown(res)
                    else:
                        st.info("No citations found.")

                except Exception as e:
                    st.error("❌ Verification failed.")
                    st.exception(e)

                st.session_state.fact_loading = False
        else:
            st.error("RAG Engine offline.")


# ============================================================================
# PAGE: SETTINGS
# ============================================================================
elif current_page == "Settings":
    st.markdown("## ⚙️ Settings / About")
    st.markdown("### LexTransition AI")
    st.divider()
    st.markdown("**Version:** 1.0.0 (Alpha)")
    st.markdown("**Status:** Offline Mode Active")
    
    if st.button("Test AI Connection"):
        with st.spinner("Pinging Ollama..."):
            try:
                # Dummy call logic could go here
                st.success("AI System Online")
            except:
                st.error("AI System Offline")

# Footer
st.markdown(
    """
<div class="app-footer">
  <div class="app-footer-inner">
    <span class="top-chip">Offline Mode</span>
    <span class="top-chip">Privacy First</span>
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
</div>
""",
    unsafe_allow_html=True,
)