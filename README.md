# LexTransition-AI

Live Demo: https://kvbgkvw4mehwhhdjt7crrg.streamlit.app/

LexTransition AI is an open-source, offline-first legal assistant. It helps users navigate the transition from old Indian laws (IPC/CrPC/IEA) to the new BNS/BNSS/BSA frameworks. Using local Machine Learning and OCR, it analyzes legal documents and maps law sections with 100% grounded accuracy.

## ⚖️ LexTransition AI: Law Mapper & Document Analyzer

LexTransition AI is an open-source, offline-first legal assistant. It helps users navigate the transition from old Indian laws (IPC/CrPC/IEA) to the new BNS/BNSS/BSA frameworks. Using local Machine Learning and OCR, it analyzes legal documents and maps law sections with 100% grounded accuracy.

## 🚀 Key Modules

- 🔄 **The Law Transition Mapper:** The core engine that maps old IPC sections to new BNS equivalents. It highlights specific changes in wording, penalties, and scope.
- 🖼️ **Multimodal Document Analysis (OCR):** Upload photos of legal notices or FIRs. The system extracts text using local OCR and explains "action items" in simple language.
- 📚 **Grounded Fact-Checking:** Every response is backed by official citations. The AI identifies the exact Section, Chapter, and Page from the official Law PDFs to prevent hallucinations.

## 🛠️ Offline Tech Stack (No-API Approach)

To ensure privacy and offline accessibility, this project can be configured to run without external APIs:

- **Backend:** Python, LangChain/LlamaIndex.
- **OCR:** EasyOCR or PyTesseract (Local engines).
- **Vector DB:** ChromaDB or FAISS (Local storage instead of Pinecone/Milvus).
- **Local LLM:** Llama 3 or Mistral via Ollama or LM Studio (Runs on your GPU/CPU).
- **Frontend:** Streamlit Dashboard.

## 📂 Project Structure

```text
LexTransition-AI/
├── app.py                 # Streamlit UI
├── requirements.txt       # Local ML libraries
├── engine/
│   ├── ocr_processor.py   # Local OCR logic
│   ├── mapping_logic.py   # IPC to BNS mapping dictionary
│   └── rag_engine.py      # Local Vector Search logic
└── models/                # Local LLM weights (Quantized)
```

## ⚙️ Installation & Local Setup

### Option A: Using Docker (Recommended)
The easiest way to run LexTransition-AI is with Docker. This handles all dependencies (including Tesseract OCR and system libraries) automatically.

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/centiceron/LexTransition-AI.git](https://github.com/centiceron/LexTransition-AI.git)
   cd LexTransition-AI

2. **Build the Docker Image**
   ```bash 
   docker build -t lextransition .

3. **Run the Application**
   ```bash
   docker run -p 8501:8501 lextransition

4. Open the App
   ```bash
   http://localhost:8501

## Current Implementation Status

- Streamlit UI (app.py) — implemented (interactive pages for Mapper, OCR, Fact-check).
- OCR — local helper supporting EasyOCR and pytesseract (install system tesseract for pytesseract).
- IPC→BNS Mapping — in-memory mapping with fuzzy match; UI supports adding mappings at runtime.
- Grounded Fact-Check — simple PDF ingestion and page-level keyword search using pdfplumber (add PDFs to ./law_pdfs via UI).
- RAG/LLM & full offline guarantees — NOT implemented yet (placeholders/stubs present).

## Quick Start (local)

- Install Python dependencies: `pip install -r requirements.txt`
- (Optional) Install Tesseract binary for pytesseract:
  - Ubuntu: `sudo apt install tesseract-ocr`
  - Mac (brew): `brew install tesseract`
- Launch: `streamlit run app.py`

To use Grounded Fact-Check, upload law PDFs in the Fact-Check page (or drop them into `./law_pdfs`) and click "Verify with Law PDFs".

## Persistence & Testing

- Mappings are persisted to `mapping_db.json` (in project root). You can add mappings in the UI; they are saved to this file.
- Run tests:
  - `pip install -r requirements.txt`
  - `pytest -q`

## Optional features (embeddings & local LLM)

### Embedding-based RAG (FAISS + sentence-transformers)

- Install (optional): `pip install sentence-transformers numpy faiss-cpu`
- Enable: `export LTA_USE_EMBEDDINGS=1`
- Index persists in `./vector_store`

### Local LLM integration (Ollama)

- Configure: `export LTA_OLLAMA_URL=http://localhost:11434`
- The app will use this endpoint for better plain-language summaries.

## CI

- A GitHub Actions workflow (lextransition-ci.yml) runs pytest for the project on PRs.

## Next Steps / TODO

- Replace page-level keyword search with embeddings + vector store (Chroma/FAISS) + exact citation offsets.
- Add persistent mapping DB + import tools for official IPC→BNS mappings.
- Integrate local LLM for summaries/explanations (Ollama / LM Studio).
- Add tests and CI for engine modules.

