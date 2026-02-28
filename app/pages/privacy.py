"""Privacy Policy page for LexTransition AI."""
import streamlit as st

def render_privacy_page():
    """Render the Privacy Policy page."""
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

- If you deploy the app (e.g. Streamlit Cloud), the hosting provider's terms and data policies apply to that deployment.
- Icons or assets loaded from CDNs (e.g. Flaticon, Simple Icons) are subject to those services' privacy policies.

### Your Rights

You control the data on your instance. You can delete uploaded PDFs and local mapping data at any time. For hosted deployments, refer to the host's data retention and deletion policies.

### Changes

We may update this policy from time to time. The "Last updated" date at the top reflects the latest revision. Continued use of the app after changes constitutes acceptance of the updated policy.

### Contact

For questions about this Privacy Policy or LexTransition AI, please open an issue or discussion on the project's GitHub repository.
""")
