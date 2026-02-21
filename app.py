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
    from engine.ocr_processor import extract_text, extract_text_batch, available_engines
    from engine.mapping_logic import map_ipc_to_bns, add_mapping
    from engine.rag_engine import search_pdfs, add_pdf, index_pdfs
    from engine.llm import summarize as llm_summarize
    from engine.db import import_mappings_from_csv, import_mappings_from_excel, export_mappings_to_json, export_mappings_to_csv
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

    # Import/Export Section
    st.markdown("### 📥 Import / 📤 Export Mappings")
    col_import, col_export = st.columns(2)

    with col_import:
        uploaded_mapping = st.file_uploader("Import from CSV/Excel", type=["csv", "xlsx"], key="mapping_upload")
        if uploaded_mapping and st.button("📥 Import Mappings", use_container_width=True):
            try:
                import tempfile
                import os
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_mapping.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_mapping.read())
                    tmp_path = tmp_file.name

                if uploaded_mapping.name.endswith('.csv'):
                    success_count, errors = import_mappings_from_csv(tmp_path)
                elif uploaded_mapping.name.endswith('.xlsx'):
                    success_count, errors = import_mappings_from_excel(tmp_path)
                else:
                    st.error("Unsupported file format")
                    success_count = 0
                    errors = ["Unsupported file format"]

                os.unlink(tmp_path)

                if success_count > 0:
                    st.success(f"✓ Successfully imported {success_count} mappings")
                if errors:
                    st.warning("Import completed with errors:")
                    for error in errors:
                        st.write(f"- {error}")

            except Exception as e:
                st.error(f"Import failed: {str(e)}")

    with col_export:
        export_format = st.selectbox("Export Format", ["JSON", "CSV"], key="export_format")
        if st.button("📤 Export Mappings", use_container_width=True):
            try:
                import tempfile
                import os
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{export_format.lower()}") as tmp_file:
                    tmp_path = tmp_file.name

                if export_format == "JSON":
                    success = export_mappings_to_json(tmp_path)
                else:
                    success = export_mappings_to_csv(tmp_path)

                if success:
                    with open(tmp_path, "rb") as f:
                        st.download_button(
                            label=f"📥 Download {export_format}",
                            data=f,
                            file_name=f"ipc_bns_mappings.{export_format.lower()}",
                            mime="application/json" if export_format == "JSON" else "text/csv",
                            use_container_width=True
                        )
                else:
                    st.error("Export failed")

                os.unlink(tmp_path)

            except Exception as e:
                st.error(f"Export failed: {str(e)}")

    st.divider()

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
    st.markdown("Extract text and key action items from legal notices, FIRs, and scanned documents. Upload multiple documents for batch processing.")
    st.divider()
    
    # Initialize session state for batch processing
    if "batch_results" not in st.session_state:
        st.session_state.batch_results = None
    if "batch_summaries" not in st.session_state:
        st.session_state.batch_summaries = {}
    if "processing_complete" not in st.session_state:
        st.session_state.processing_complete = False
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Upload Legal Documents")
        st.markdown("**Single or Multiple Files Supported**")
        uploaded_files = st.file_uploader(
            "Upload (FIR/Notice)", 
            type=["jpg", "png", "jpeg"], 
            accept_multiple_files=True,
            label_visibility="collapsed",
            key="batch_uploader"
        )
        
        if uploaded_files:
            st.markdown(f"**{len(uploaded_files)} file(s) selected**")
            
            # Show processing queue with status indicators
            st.markdown("### Processing Queue")
            for i, file in enumerate(uploaded_files):
                status = "Pending"
                if st.session_state.batch_results and file.name in st.session_state.batch_results:
                    result = st.session_state.batch_results[file.name]
                    status = "Complete" if result['status'] == 'success' else "Error"
                st.markdown(f"- **{file.name}**: {status}")
    
    with col2:
        if uploaded_files:
            # Process button
            process_btn = st.button("Extract & Analyze All", use_container_width=True, key="batch_process_btn")
            
            if process_btn and ENGINES_AVAILABLE:
                # Create progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Initialize results storage
                results = {}
                summaries = {}
                total_files = len(uploaded_files)
                
                # Process each file with progress updates
                for i, file in enumerate(uploaded_files):
                    status_text.text(f"Processing: {file.name} ({i+1}/{total_files})")
                    progress_bar.progress((i + 1) / total_files)
                    
                    try:
                        # Reset file pointer and read
                        file.seek(0)
                        raw = file.read()
                        extracted = extract_text(raw)
                        
                        # Get summary
                        summary = llm_summarize(extracted, question="What actions should the user take?")
                        
                        results[file.name] = {
                            'text': extracted,
                            'status': 'success',
                            'error': None
                        }
                        summaries[file.name] = summary
                    except Exception as e:
                        results[file.name] = {
                            'text': '',
                            'status': 'error',
                            'error': str(e)
                        }
                        summaries[file.name] = None
                
                # Store results in session state
                st.session_state.batch_results = results
                st.session_state.batch_summaries = summaries
                st.session_state.processing_complete = True
                
                # Complete the progress
                progress_bar.progress(100)
                status_text.text("Processing complete!")
                
            # Display results
            if st.session_state.batch_results and st.session_state.processing_complete:
                st.markdown("---")
                st.markdown("### Results")
                
                # Download All Summaries button
                if st.session_state.batch_summaries:
                    # Combine all summaries
                    combined_summary = "=" * 50 + "\n"
                    combined_summary += "BATCH OCR PROCESSING - ALL SUMMARIES\n"
                    combined_summary += "=" * 50 + "\n\n"
                    
                    for filename, summary in st.session_state.batch_summaries.items():
                        combined_summary += f"--- {filename} ---\n"
                        if summary:
                            combined_summary += f"{summary}\n"
                        else:
                            combined_summary += "No summary available\n"
                        combined_summary += "\n"
                    
                    st.download_button(
                        label="Download All Summaries",
                        data=combined_summary,
                        file_name="all_document_summaries.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
                # Display expandable cards for each document
                for filename, result in st.session_state.batch_results.items():
                    with st.expander(f"Document: {filename}", expanded=True):
                        if result['status'] == 'success':
                            st.markdown(f"**Status:** Processed Successfully")
                            
                            # Show extracted text
                            with st.expander("Extracted Text"):
                                st.code(result['text'], language="text")
                            
                            # Show summary
                            summary = st.session_state.batch_summaries.get(filename)
                            if summary:
                                with st.expander("Action Items"):
                                    st.markdown(summary)
                        else:
                            st.markdown(f"**Status:** Error")
                            st.error(f"Error: {result.get('error', 'Unknown error')}")
                
                # Aggregate action items section
                st.markdown("---")
                st.markdown("### Aggregate Action Items")
                
                all_summaries = [s for s in st.session_state.batch_summaries.values() if s]
                if all_summaries:
                    # Combine all summaries for aggregate view
                    combined_text = "\n\n".join(all_summaries)
                    aggregate_summary = llm_summarize(
                        combined_text, 
                        question="What are ALL the action items the user needs to take across all documents? List them clearly."
                    )
                    if aggregate_summary:
                        st.markdown(aggregate_summary)
                    else:
                        # Fallback to listing all individual summaries
                        for i, summary in enumerate(all_summaries, 1):
                            st.markdown(f"**Document {i}:** {summary}")
                else:
                    st.info("No action items available from processed documents.")
            
            # Engine info
            if ENGINES_AVAILABLE and not st.session_state.processing_complete:
                engines = available_engines()
                st.info(f"OCR Engines: {', '.join(engines) if engines else 'Default'}")
            
            # Fallback for non-engine mode
            if not ENGINES_AVAILABLE and uploaded_files and st.button("Extract & Analyze All", use_container_width=True, key="fallback_batch"):
                # Demo results for testing without OCR
                st.session_state.batch_results = {
                    f.name: {
                        'text': "NOTICE UNDER SECTION 41A CrPC... (OCR not configured). Install easyocr/pytesseract & tesseract binary for production.",
                        'status': 'success',
                        'error': None
                    } for f in uploaded_files
                }
                st.session_state.batch_summaries = {
                    f.name: "The police want you to join the investigation. No immediate arrest required." for f in uploaded_files
                }
                st.session_state.processing_complete = True
                st.rerun()
            
            # Clear results button
            if st.session_state.processing_complete:
                if st.button("Clear Results", use_container_width=True):
                    st.session_state.batch_results = None
                    st.session_state.batch_summaries = {}
                    st.session_state.processing_complete = False
                    st.rerun()

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
