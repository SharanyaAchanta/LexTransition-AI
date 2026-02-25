"""FAQ page for LexTransition AI."""
import streamlit as st

def render():
    """Render the FAQ page."""
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
When run locally with default settings, **no**. Documents, section queries, and uploads are processed on your machine. Local OCR and local LLM (e.g. Ollama) keep everything offline. If you use a hosted version (e.g. Streamlit Cloud), that provider's infrastructure and policies apply.
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
Mappings are stored in **`mapping_db.json`** in the project root. You can edit this file or use the Mapper UI to add/update entries. For bulk updates, use the engine's import/export utilities (e.g. CSV/Excel) if available in your build.
""")
