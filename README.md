# LexTransition-AI

Live Demo: https://kvbgkvw4mehwhhdjt7crrg.streamlit.app/

LexTransition AI is an open-source, offline-first legal assistant. It helps users navigate the transition from old Indian laws (IPC/CrPC/IEA) to the new BNS/BNSS/BSA frameworks. Using local Machine Learning and OCR, it analyzes legal documents and maps law sections with 100% grounded accuracy.

---

## ⚖️ LexTransition AI: Law Mapper & Document Analyzer

LexTransition AI is an open-source, offline-first legal assistant. It helps users navigate the transition from old Indian laws (IPC/CrPC/IEA) to the new BNS/BNSS/BSA frameworks. Using local Machine Learning and OCR, it analyzes legal documents and maps law sections with 100% grounded accuracy.

---

### 🚀 Key Modules

## 🚀 Core Features

- 🔄 **Intelligent Law Mapper:** Maps old IPC sections to new BNS equivalents. Uses an LLM to highlight specific changes in wording, penalties, and scope.
- 🖼️ **Multimodal OCR Analysis:** Upload photos of legal notices or FIRs. The system extracts text using local OCR and generates actionable summaries.
- 📚 **Grounded Fact-Checking (RAG):** Ask legal questions and get answers backed by official citations. The AI identifies the exact Section and Page from uploaded Law PDFs to prevent hallucinations.
- 🎙️ **Offline Voice Agent:** Features an integrated Text-to-Speech (TTS) engine that provides high-fidelity vocal dictations of summaries, action items, and fact-checks.

---

## 🛠️ Offline Tech Stack (No-API Approach)

To ensure privacy and offline accessibility, this project can be configured to run without external APIs:

- **Frontend:** Streamlit
- **Backend:** Python, LangChain/LlamaIndex.
- **Local LLM Engine:** Ollama (Llama 3 / Mistral)
- **Voice / TTS:** Piper TTS (ONNX models)
- **OCR Engine:** EasyOCR / PyTesseract
- **Vector Database (RAG):** FAISS + Sentence-Transformers

---

## 📂 Project Structure

```css
LexTransition-AI/
├── .github/
│   └── workflows/
│       └── lextransition-ci.yml  # GitHub Actions CI/CD pipeline
├── engine/
│   ├── comparator.py             # AI logic for comparing IPC & BNS texts
│   ├── llm.py                    # Fallback logic and LLM summarization
│   ├── mapping_logic.py          # Core IPC to BNS transition logic
│   ├── ocr_processor.py          # Local OCR extraction and processing
│   ├── rag_engine.py             # Local Vector Search logic (FAISS)
│   └── db.py                     # Database connection and queries
├── utils/
│   └── timeout_handler.py        # Resiliency and API timeout handlers
├── tests/
│   └── test_embeddings.py        # Pytest suite for automated testing
├── scripts/
│   └── ocr_benchmark.py          # OCR character error rate testing
├── models/
│   └── tts/                      # Local storage for Piper ONNX voice models
├── law_pdfs/                     # Upload directory for Grounded Fact-Checking
├── app.py                        # Main Streamlit UI application
├── Dockerfile                    # Production container configuration
├── requirements.txt              # Python dependencies & OS-specific markers
├── setup_agent.py                # Manual setup script for downloading TTS binaries
└── README.md                     # Master project documentation
```
---

## ⚙️ Installation & Local Setup

### Option A: Using Docker (Recommended)
The easiest way to run LexTransition-AI is with Docker. This handles all dependencies (including Tesseract OCR and system libraries) automatically.

1. **Clone the repository:**

   ```bash
   git clone [https://github.com/[username]/LexTransition-AI.git](https://github.com/[username]/LexTransition-AI.git)
   cd LexTransition-AI
   ```

2. **Build the Docker Image in terminal**

   ```bash 
   docker build -t lextransition .
   ```

3. **Run the Application**

   ```bash
   docker run -p 8501:8501 -e LTA_OLLAMA_URL="[http://host.docker.internal:11434](http://host.docker.internal:11434)" lextransition-ai
   ```

4. **Open the App**

   ```bash
   http://localhost:8501
   ```
---

### Option B: Manual Local Setup (Windows/Linux/Mac)
If you prefer to run the app directly in your local Python environment:

1. **Install Dependencies (_requires Python 3.10_)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Download Voice Agent Models**

   ```bash 
   python setup_agent.py
   ```

3. **Start the Local LLM**

   ```bash
   ollama serve
   ollama pull llama3
   ```

4. **Launch the App**

   ```bash
   export LTA_OLLAMA_URL="http://localhost:11434"  # On Windows use: set LTA_OLLAMA_URL=http://localhost:11434
   streamlit run app.py
   ```
---

## 🟢 Current Implementation Status & Architecture

All core modules, offline LLM integrations, and containerization features are **fully implemented and production-ready**.

```text
   =========================================================================
                  🚀 LEXTRANSITION-AI: SYSTEM ARCHITECTURE
   =========================================================================

                  [ 🖥️ Streamlit Frontend (app.py) ]
                                 |
         -------------------------------------------------
         |                       |                       |
   [ 🔄 IPC → BNS Mapper ]  [ 🖼️ Document OCR ]   [ 📚 Fact-Checker (RAG) ]
         |                       |                       |
   (SQLite Mapping DB)    (EasyOCR / PyTesseract)  (FAISS + sentence-transformers)
         |                       |                       |
         -------------------------------------------------
                                 |
                                 v
                  [ 🧠 Local LLM Engine (Ollama) ]
            (Semantic Analysis, Action Items, Summarization)
                                 |
                                 v
                  [ 🎙️ Offline Voice Agent (Piper TTS) ]
            (High-fidelity vocal dictation of AI outputs)

   =========================================================================
                     ⚙️ INFRASTRUCTURE GUARANTEES
   =========================================================================
   ✔️ 100% Offline Capable (No external API keys required)
   ✔️ Dockerized Deployment (Verified networking & TTS dependencies)
   ✔️ CI/CD Pipeline Active (GitHub Actions + Pytest)
```
---

## 💾 Data Persistence & Testing

1. **Local Data Storage (Privacy-First)**
To maintain our strict offline-first architecture, no user data or legal documents ever leave your machine:
- **Relational Data:** Mappings and system configurations are persisted securely using a local SQLite database (replacing the legacy `mapping_db.json`).
- **Vector Store:** Uploaded law PDFs for Grounded Fact-Checking are processed and stored locally in a FAISS vector index (`./vector_store`).

2. **Automated Testing & CI/CD**
LexTransition-AI maintains high reliability through local testing and GitHub Actions.

   **Local Unit Tests**
   To run the test suite locally, ensure your virtual environment is active (Python 3.10) and execute:

   ```bash
   pip install -r requirements.txt
   pytest -q
   ```
---

## Continuous Integration (GitHub Actions)
   Every Pull Request automatically triggers our `.github/workflows/lextransition-ci.yml` pipeline.   

---

## OCR Benchmark Harness

To evaluate the local OCR engine's Character Error Rate (CER) and Keyword Recall against custom scanned datasets

   ```bash
   python scripts/ocr_benchmark.py --dataset data/ocr_dataset.csv --report ocr_report.md
   ```
---

## ⚙️ Advanced Configuration (Environment Variables)

LexTransition-AI is designed to be plug-and-play, but power users can customize the engine behavior using environment variables. If you are using Docker, these are passed via the `-e` flag.

| Variable | Default | Description |
| :--- | :--- | :--- |
| `LTA_OLLAMA_URL` | `http://localhost:11434` | The endpoint for the local LLM. When running in Docker, use `http://host.docker.internal:11434` to route traffic to your host machine. |
| `LTA_OLLAMA_MODEL` | `llama3` | Specifies which local model to use for analysis and summarization. |
| `LTA_USE_EMBEDDINGS` | `1` | Toggles the FAISS/Sentence-Transformer RAG engine. Set to `0` to fallback to legacy keyword search. |

---

## 🗺️ Project Roadmap & Future Scope

All foundational features (Local LLM, OCR, Vector DB, and CI/CD) are fully operational. The next phase of development focuses on expanding accessibility and enterprise utility:

- [ ] **Speech-to-Text (STT) Integration:** Implement local Whisper models to allow users to verbally query the Fact-Checker without typing.
- [ ] **Multilingual Support (Indic Languages):** Translate BNS mappings and OCR summaries into Hindi, Bengali, and other regional languages for broader accessibility.
- [ ] **Precedent & Case Law Expansion:** Expand the RAG Vector Database beyond standard Bare Acts to include landmark judicial precedents.
- [ ] **Automated Legal Briefs:** Add a reporting engine to export OCR analysis and IPC-to-BNS comparisons into cleanly formatted PDF/Docx files.

---