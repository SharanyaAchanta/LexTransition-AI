"""FAQ page for LexTransition AI."""
import streamlit as st
from engine.github_stats import get_github_contributors

def render_faq_page():
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