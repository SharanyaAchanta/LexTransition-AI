import streamlit as st
import os
import html as html_lib
import re

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

# URL-based navigation (clickable cards via ?page=...) with sidebar precedence

def _read_url_page():
    """Return page from query params in a version-agnostic way, or None."""
    try:
        # Preferred modern API
        qp = st.query_params  # type: ignore[attr-defined]
        # qp may not support .get in all versions
        try:
            val = qp.get("page", None)
        except Exception:
            # Try dict conversion
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
current_page = st.session_state.current_page



# ============================================================================
# PAGE: HOME
# ============================================================================
if current_page == "Home":
    # Header Section
    st.markdown('<div class="home-header">', unsafe_allow_html=True)
    st.markdown('<div class="home-title">⚖️ LexTransition AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="home-subtitle">'
        'Your offline legal assistant powered by AI. Analyze documents, map sections, and get instant legal insights—no internet required, your data stays private.'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # What do you want to do? Section
    st.markdown('<div class="home-what">What do you want to do?</div>', unsafe_allow_html=True)
    
    # Two column layout for cards
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("""
        <a class="home-card" href="?page=Mapper" target="_self">
            <div class="home-card-header">
                <span class="home-card-icon">✓</span>
                <div class="home-card-title">Convert IPC to BNS</div>
            </div>
            <div class="home-card-desc">Map old IPC sections to new BNS equivalents.</div>
            <div class="home-card-btn">
                <span>Open Mapper</span>
                <span>›</span>
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <a class="home-card" href="?page=OCR" target="_self">
            <div class="home-card-header">
                <span class="home-card-icon">📄</span>
                <div class="home-card-title">Analyze FIR / Notice</div>
            </div>
            <div class="home-card-desc">Extract text and key action points from legal documents.</div>
            <div class="home-card-btn">
                <span>Upload & Analyze</span>
                <span>›</span>
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    # Spacer
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Second row
    col3, col4 = st.columns(2, gap="large")
    
    with col3:
        st.markdown("""
        <a class="home-card" href="?page=Fact" target="_self">
            <div class="home-card-header">
                <span class="home-card-icon">📚</span>
                <div class="home-card-title">Legal Research</div>
            </div>
            <div class="home-card-desc">Search and analyze case law and statutes.</div>
            <div class="home-card-btn">
                <span>Start Research</span>
                <span>›</span>
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <a class="home-card" href="?page=Settings" target="_self">
            <div class="home-card-header">
                <span class="home-card-icon">⚙️</span>
                <div class="home-card-title">Settings</div>
            </div>
            <div class="home-card-desc">Configure engines and settings.</div>
            <div class="home-card-btn">
                <span>Configure</span>
                <span>›</span>
            </div>
        </a>
        """, unsafe_allow_html=True)

# ============================================================================
# PAGE: IPC TO BNS MAPPER
# ============================================================================
elif current_page == "Mapper":
    st.markdown("## ✓ IPC → BNS Transition Mapper")
    st.markdown("Convert old IPC sections into new BNS equivalents with legal-grade accuracy.")
    st.divider()
    
    # Input Section (wrapped)
    st.markdown('<div class="mapper-wrap">', unsafe_allow_html=True)
    col1, col2 = st.columns([4, 1])
    with col1:
        search_query = st.text_input("Enter IPC Section", placeholder="e.g., 420, 302, 378")
    with col2:
        search_btn = st.button("🔍 Find BNS Eq.", use_container_width=True)
    
    # Results Section
    if search_query and search_btn:
        if ENGINES_AVAILABLE:
            result = map_ipc_to_bns(search_query.strip())
            if result:
                # Styled result card
                ipc = search_query.strip()
                bns = result.get("bns_section", "N/A")
                notes = result.get("notes", "See source mapping.")
                source = result.get("source", "mapping_db")

                ipc_html = html_lib.escape(str(ipc))
                bns_html = html_lib.escape(str(bns))
                notes_html = html_lib.escape(str(notes))
                source_html = html_lib.escape(str(source))

                st.markdown(f"""
                <div class="result-card">
                    <div class="result-badge">Mapping • <span style="opacity:0.9">found</span></div>
                    <div class="result-grid">
                        <div class="result-col">
                            <div class="result-col-title">IPC Section</div>
                            <div style="font-size:20px;font-weight:700;color:var(--text-color);margin-top:6px;">{ipc_html}</div>
                        </div>
                        <div class="result-col">
                            <div class="result-col-title">BNS Section</div>
                            <div style="font-size:20px;font-weight:700;color:var(--primary-color);margin-top:6px;">{bns_html}</div>
                        </div>
                    </div>
                    <ul class="result-list">
                        <li>{notes_html}</li>
                        <li>Verify against official text before relying on it</li>
                    </ul>
                    <div style="position:absolute;left:14px;bottom:14px;font-size:12px;opacity:0.8;color:var(--text-color);">Source: {source_html}</div>
                </div>
                """, unsafe_allow_html=True)

                # Functional action buttons (styled to sit inside the result card)
                if st.button("Compare Side-By-Side", key="compare_side"):
                    st.info("Opening comparison view...")
                if st.button("View Legal Text", key="view_legal_text"):
                    st.info("Opening legal text viewer...")

                # Summarize button
                if st.button("📝 Summarize", key="summarize_mapping"):
                    summary_text = llm_summarize(notes, question=f"What are the key changes from IPC {ipc} to BNS {bns}?")
                    if summary_text:
                        with st.expander("📝 Plain-Language Summary"):
                            st.markdown(summary_text)
                    else:
                        st.warning("Summary unavailable. LLM not configured or failed.")

                st.divider()
            else:
                st.warning("⚠️ Section not found in mapping")
                with st.expander("➕ Add New Mapping"):
                    ipc = st.text_input("IPC Section", value=search_query)
                    bns = st.text_input("BNS Section (e.g., BNS 318)")
                    notes = st.text_area("Key Changes / Notes")
                    if st.button("✓ Save Mapping", use_container_width=True):
                        add_mapping(ipc, bns, notes, source="user")
                        st.success("✓ Mapping saved successfully!")
        else:
            if search_query == "420":
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### IPC Section")
                    st.markdown("**420** (Cheating)")
                with col2:
                    st.markdown("### BNS Section")
                    st.markdown("**318**")
                st.divider()
                st.markdown("### Key Changes")
                st.markdown("• Offence of cheating retained")
                st.markdown("• Penalty wording updated")
                st.markdown("• Scope expanded to digital fraud")
            else:
                st.error("Section not found in database")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# PAGE: DOCUMENT OCR
# ============================================================================
elif current_page == "OCR":
    st.markdown("## 🖼️ Document OCR")
    st.markdown("Extract text and key action items from legal notices, FIRs, and scanned documents.")
    st.divider()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Upload a legal Document")
        uploaded_file = st.file_uploader("Upload (FIR/Notice)", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        
        if uploaded_file:
            st.markdown("### Preview")
            st.image(uploaded_file, use_column_width=True)
    
    with col2:
        if uploaded_file:
            st.markdown("### Extracted Text")
            if st.button("🔧 Extract & Analyze", use_container_width=True):
                if ENGINES_AVAILABLE:
                    raw = uploaded_file.read()
                    extracted = extract_text(raw)
                    st.code(extracted, language="text")
                    
                    # Try LLM summary
                    summary = llm_summarize(extracted, question="What actions should the user take?")
                    if summary:
                        with st.expander("📝 Simplified Action Item"):
                            st.markdown(summary)
                else:
                    st.code("NOTICE UNDER SECTION 41A CrPC...", language="text")
                    st.markdown("**Simplified Action Item:** The police want you to join the investigation. No immediate arrest required.")
            
            # Engine info
            if ENGINES_AVAILABLE:
                engines = available_engines()
                st.info(f"✓ OCR Engines: {', '.join(engines) if engines else 'Default'}")

# ============================================================================
# PAGE: GROUNDED FACT CHECKER
# ============================================================================
elif current_page == "Fact":
    st.markdown("## 📚 Grounded Fact Checker")
    st.markdown("Ask a legal question to verify answers with citations from official PDFs.")
    st.divider()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        user_question = st.text_input("What is the penalty for…", placeholder="e.g., cheating under the new BNS system?")
    with col2:
        search_btn = st.button("📖 Verify", use_container_width=True)
    
    # PDF Upload Section
    st.markdown("### Upload Law PDF to Corpus (optional)")
    uploaded_pdf = st.file_uploader("Drop PDFs here", type=["pdf"], label_visibility="collapsed")
    if uploaded_pdf:
        save_dir = "law_pdfs"
        os.makedirs(save_dir, exist_ok=True)
        safe_name = _safe_filename(uploaded_pdf.name, default="law.pdf")
        dest_path = _dedupe_path(os.path.join(save_dir, safe_name))
        with open(dest_path, "wb") as f:
            f.write(uploaded_pdf.read())
        if ENGINES_AVAILABLE:
            add_pdf(dest_path)
        st.success(f"✓ '{os.path.basename(dest_path)}' added to corpus")
    
    st.divider()
    
    # Results Section
    if user_question and search_btn:
        st.markdown("### Citation")
        if ENGINES_AVAILABLE:
            res = search_pdfs(user_question or "")
            if res:
                st.markdown(res)
                # optional: summarize
                combined = "\n\n".join([line for line in res.split("\n") if line.startswith(">   > _")])
                summary = llm_summarize(combined, question=user_question)
                if summary:
                    with st.expander("📝 Summary (Plain Language)"):
                        st.markdown(summary)
            else:
                st.info("ℹ️ No citations found. Add PDFs to law_pdfs/ folder to enable search.")
        else:
            st.markdown("> **Example output (engine disabled):**")
            st.markdown("> - Add official PDFs to `law_pdfs/` and click **Verify** to get grounded citations.")

# ============================================================================
# PAGE: SETTINGS / ABOUT
# ============================================================================
elif current_page == "Settings":
    st.markdown("## ⚙️ Settings / About")
    st.markdown("### LexTransition AI")
    st.markdown("Offline legal assistant for mapping agents, the transition from IPC/CrPC/IEA to the new BNS/BNSS/BSA frameworks.")
    st.divider()
    st.markdown("**Version:** 1.0.0")
    st.markdown("**License:** Open Source")
    st.markdown("**Privacy:** 100% Offline - No data sent to servers")

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
