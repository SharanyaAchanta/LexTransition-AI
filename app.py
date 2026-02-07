import streamlit as st
import os

# Page Configuration
st.set_page_config(page_title="LexTransition AI", page_icon="⚖️", layout="wide")

# Custom Styling
st.markdown("""
    <style>
    .main-title { font-size: 38px; font-weight: bold; color: #1E3A8A; text-align: center; }
    .sub-text { font-size: 18px; text-align: center; color: #555; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #1E3A8A; color: white; }
    </style>
    """, unsafe_allow_html=True)

# Sidebar Navigation with Icons
st.sidebar.title("⚖️ LexTransition AI")
st.sidebar.info("Offline Legal Assistant: Mapping IPC to BNS")
role = st.sidebar.radio("Go to:", ["🏠 Home", "🔄 Law Mapper", "🖼️ OCR Document Analysis", "📚 Grounded Fact-Check"])

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
if ENGINES_AVAILABLE:
    try:
        index_pdfs("law_pdfs")
    except Exception:
        pass

# --- 1. HOME PAGE ---
if role == "🏠 Home":
    st.markdown('<p class="main-title">LexTransition AI</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-text">Bridging the gap between IPC (Old) and BNS (New) Laws</p>', unsafe_allow_html=True)
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("### 1. Transition Mapper\nMaps IPC sections to BNS equivalents instantly.")
    with col2:
        st.success("### 2. OCR Analysis\nExtracts text from legal notices and FIR photos.")
    with col3:
        with st.expander("### 3. Fact Checking"):
            st.write("Ensures 100% accuracy with PDF citations.")

# --- 2. LAW MAPPER ---
elif role == "🔄 Law Mapper":
    st.header("🔄 IPC to BNS Transition Mapper")
    st.write("Search for an old IPC section to find its new BNS counterpart.")
    
    search_query = st.text_input("Enter IPC Section (e.g., 420, 302, 378):")
    
    if search_query:
        if ENGINES_AVAILABLE:
            result = map_ipc_to_bns(search_query.strip())
            if result:
                st.warning(f"### Old Law: IPC Section {search_query}")
                st.success(f"### New Law: {result['bns_section']}")
                st.write(f"**Key Changes:** {result.get('notes','See source mapping.')}")
                st.caption(f"Source: {result.get('source','mapping_db')}")
            else:
                st.error("Section not found in mapping. You can add it below.")
                with st.expander("Add Mapping"):
                    ipc = st.text_input("IPC Section", value=search_query)
                    bns = st.text_input("BNS Section (e.g., BNS 318)")
                    notes = st.text_area("Notes / Summary")
                    if st.button("Add Mapping"):
                        add_mapping(ipc, bns, notes, source="user")
                        st.success("Mapping added (in-memory). Restart app to persist.")
        else:
            # static demo retained for now
            if search_query == "420":
                st.warning("### Old Law: IPC Section 420 (Cheating)")
                st.success("### New Law: BNS Section 318")
                st.write("**Key Changes:** The punishment remains similar, but the section numbering and sub-clauses have been reorganized for better clarity under BNS.")
            else:
                st.error("Section not found in static database. AI Model will process this in the full version.")

# --- 3. OCR ANALYSIS ---
elif role == "🖼️ OCR Document Analysis":
    st.header("🖼️ Multimodal Document Analysis")
    st.write("Upload a photo of a legal document to extract and simplify text.")
    
    uploaded_file = st.file_uploader("Upload Image (FIR/Notice)", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Document", width=400)
        if st.button("Extract & Explain"):
            if ENGINES_AVAILABLE:
                raw = uploaded_file.read()
                extracted = extract_text(raw)
                st.code(f"Extracted Text: {extracted}")
                # try LLM summary
                summary = llm_summarize(extracted, question="What actions should the user take?")
                if summary:
                    st.success("**Simplified Action Item:**")
                    st.write(summary)
                else:
                    st.success("**Simplified Action Item:** (Install/configure local LLM for automatic summaries)")
            else:
                st.info("OCR Engine (EasyOCR/Tesseract) is processing... [Static Demo]")
                st.code("Extracted Text: NOTICE UNDER SECTION 41A CrPC...")
                st.success("**Simplified Action Item:** The police want you to join the investigation. No immediate arrest, but you must appear at the station.")
        else:
            if ENGINES_AVAILABLE:
                engines = available_engines()
                st.caption(f"Available OCR engines: {', '.join(engines) if engines else 'None (install easyocr/pytesseract)'}")

# --- 4. FACT-CHECK ---
elif role == "📚 Grounded Fact-Check":
    st.header("📚 Grounded Fact-Checking")
    st.write("Ask a legal question to get answers with official citations.")
    
    user_question = st.text_input("Ask a legal question:")
    uploaded_pdf = st.file_uploader("Upload Law PDF to Corpus (optional)", type=["pdf"])
    if uploaded_pdf:
        save_dir = "law_pdfs"
        os.makedirs(save_dir, exist_ok=True)
        dest_path = os.path.join(save_dir, uploaded_pdf.name)
        with open(dest_path, "wb") as f:
            f.write(uploaded_pdf.read())
        if ENGINES_AVAILABLE:
            add_pdf(dest_path)
            st.success(f"PDF '{uploaded_pdf.name}' added to corpus.")
        else:
            st.info("Upload saved locally but search engine not configured (install pdfplumber).")

    embed_toggle = st.checkbox("Use embedding-based search (if enabled)", value=True)
    if st.button("Verify with Law PDFs"):
        if ENGINES_AVAILABLE:
            if embed_toggle and os.environ.get("LTA_USE_EMBEDDINGS") == "1":
                res = search_pdfs(user_question or "")
            else:
                res = search_pdfs(user_question or "")
            if res:
                st.markdown(res)
                # optional: summarize combined snippets via LLM
                combined = "\n\n".join([line for line in res.split("\n") if line.startswith(">   > _")])
                summary = llm_summarize(combined, question=user_question)
                if summary:
                    st.markdown("**Summary (plain language):**")
                    st.write(summary)
            else:
                st.write("No matching citations found in local PDFs. Add PDFs above to the 'law_pdfs' folder and re-index.")
        else:
            st.write("Searching through BNS Official Gazette... (Static demo)")
            st.markdown("""
            > **Answer:** Under BNS, theft is defined under Section 303.
            > 
            > **Citation:** > - **Source:** BNS_Official_Gazette.pdf
            > - **Chapter:** XVII (Offences Against Property)
            > - **Page No:** 84
            """)