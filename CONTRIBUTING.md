# 👋 Contributing to LexTransition-AI

Welcome, and thank you for your interest in contributing to **LexTransition-AI**! Whether you're a student, an experienced developer, or someone passionate about legal-tech and NLP, we're thrilled to have you here.

LexTransition-AI is an open-source, offline-first legal assistant designed to help users navigate the transition from old Indian laws (IPC/CrPC/IEA) to the new BNS/BNSS/BSA frameworks. Your contributions help make legal technology more accessible to everyone.

---

## 📋 Table of Contents

- [🐍 Development Environment Setup](#-development-environment-setup)
- [🧠 Model & Data Setup](#-model--data-setup)
- [🔄 Contribution Workflow](#-contribution-workflow)
- [📝 Code Style](#-code-style)
- [🐛 Issue Reporting](#-issue-reporting)

---

## 🐍 Development Environment Setup

### Prerequisites:

> Before you begin, ensure you have the following installed:

| Tool | Version | Purpose |
|------|---------|---------|
| **Python** | 3.8+ | Core runtime |
| **Git** | Latest | Version control |
| **pip** | Latest | Package management |
| **Ollama** | Latest | Required for Local LLM & Embeddings |
| **Tesseract OCR** | Latest | *(Optional)* For pytesseract support |

---

### Step 1: Fork & Clone the Repository

```bash
# Fork the repo on GitHub, then clone your fork
git clone https://github.com/<your-username>/LexTransition-AI.git
cd LexTransition-AI
```
---

### Step 2: Create a Virtual Environment

Using a virtual environment is **critical** for this project to:
- Isolate project dependencies from your system Python
- Prevent conflicts between different ML library versions
- Ensure reproducible development environments

<details>
<summary><strong>🐧 Linux / macOS</strong></summary>

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Verify activation (should show venv path)
which python
```

</details>

<details>
<summary><strong>🪟 Windows (PowerShell)</strong></summary>

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Verify activation
where python
```

</details>

<details>
<summary><strong>🪟 Windows (Command Prompt)</strong></summary>

```powershell
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate.bat

# Verify activation
where python
```

</details>

---

### Step 3: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```
---

### Current dependencies include:
- `streamlit>=1.15` — Web UI framework
- `pillow` — Image processing
- `pdfplumber` — PDF text extraction
- `pytest` — Testing framework
- `reportlab` — PDF generation
- `requests` — HTTP library

---

### Step 4: (Optional) Install OCR Dependencies

> For full OCR functionality with `pytesseract`:

```bash
# Ubuntu/Debian
sudo apt install tesseract-ocr

# macOS (Homebrew)
brew install tesseract

# Windows — Download installer from:
# https://github.com/UB-Mannheim/tesseract/wiki
```
---

### Step 5: (Optional) Install Embedding & RAG Dependencies

> For embedding-based RAG functionality:

```bash
pip install sentence-transformers numpy faiss-cpu
```
---

## 🧠 Model & Data Setup

### Running the Application

```bash
# Launch the Streamlit app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

### Project Structure Overview

```css
LexTransition-AI/
├── app.py                 # Streamlit UI (main entry point)
├── requirements.txt       # Python dependencies
├── mapping_db.json        # Persisted IPC→BNS mappings
├── engine/                # Core processing modules
│   ├── ocr_processor.py   # Local OCR logic
│   ├── mapping_logic.py   # IPC to BNS mapping
│   ├── rag_engine.py      # Vector search logic
│   ├── llm.py             # LLM integration
│   └── embeddings_engine.py # Embedding processing
├── law_pdfs/              # Legal PDF documents
├── models/                # Local LLM weights (if using)
├── vector_store/          # FAISS index storage
└── tests/                 # Test suite
```
---

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `LTA_USE_EMBEDDINGS` | Enable embedding-based RAG | `export LTA_USE_EMBEDDINGS=1` |
| `LTA_OLLAMA_URL` | Local LLM endpoint (Ollama) | `export LTA_OLLAMA_URL=http://localhost:11434` |

---

### Using the Fact-Check Feature

1. Upload law PDFs in the Fact-Check page, or place them in `./law_pdfs/`
2. Click **"Verify with Law PDFs"** to ground-check responses

---

## 🔄 Contribution Workflow

### Branch Naming Convention

> Use descriptive prefixes for your branches:

| Prefix | Use Case | Example |
|--------|----------|---------|
| `feat/` | New features | `feat/add-bsa-mappings` |
| `fix/` | Bug fixes | `fix/ocr-encoding-error` |
| `docs/` | Documentation updates | `docs/improve-readme` |
| `refactor/` | Code refactoring | `refactor/engine-module` |
| `test/` | Test additions/updates | `test/add-mapper-tests` |

---

### Step-by-Step Process

1. **Create a feature branch**
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make your changes**
   - Write clean, documented code
   - Add tests for new functionality
   - Update documentation as needed

3. **Run tests locally**
   ```bash
   pytest -q
   ```

4. **Commit with clear messages**
   ```bash
   git add .
   git commit -m "feat: add support for BSA section parsing"
   ```

   **Commit message format:**
   - `feat:` — New features
   - `fix:` — Bug fixes
   - `docs:` — Documentation changes
   - `test:` — Test additions/updates
   - `refactor:` — Code refactoring

5. **Push and create a Pull Request**
   ```bash
   git push origin feat/your-feature-name
   ```
   
   Then open a PR on GitHub with:
   - Clear description of changes
   - Reference to any related issues
   - Screenshots for UI changes

---

## 📝 Code Style

### Python Standards

> We follow **PEP 8** guidelines. Please ensure your code:

- Uses **4 spaces** for indentation (no tabs)
- Limits lines to **88 characters** (Black formatter default)
- Uses **snake_case** for functions and variables
- Uses **PascalCase** for class names
- Includes **docstrings** for functions and classes

---

### Code Quality Checklist

```python
# ✅ Good: Clear function with docstring and type hints
def map_ipc_to_bns(section: str) -> dict:
    """
    Maps an IPC section to its BNS equivalent.
    
    Args:
        section: The IPC section number (e.g., "302")
    
    Returns:
        A dictionary containing the mapped BNS section and details.
    """
    # Implementation here
    pass

# ❌ Bad: No documentation, unclear variable names
def map(s):
    x = db[s]
    return x
```
---

### Comments in AI/ML Code

> For complex algorithms and model logic, **please add explanatory comments**:

```python
# Compute cosine similarity between query embedding and document embeddings
# Higher scores indicate more semantic similarity
similarities = np.dot(query_embedding, doc_embeddings.T)

# Apply softmax to normalize scores into probability distribution
# This helps with ranking and threshold-based filtering
probabilities = softmax(similarities)
```
---

### Recommended Tools

```bash
# Format code with Black
pip install black
black .

# Check style with flake8
pip install flake8
flake8 --max-line-length=88 .
```
---

## 🐛 Issue Reporting

### Before Reporting

1. Check if the issue already exists in [GitHub Issues](https://github.com/SharanyaAchanta/LexTransition-AI/issues)
2. Try reproducing the issue with the latest `main` branch
3. Gather relevant logs and screenshots

---

### Issue Template

> When creating an issue, please include:

```markdown
## 🐛 Bug Report

### Description
<!-- A clear description of the bug -->

### Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

### Expected Behavior
<!-- What should happen -->

### Actual Behavior
<!-- What actually happens -->

### Environment
- **OS:** [e.g., Ubuntu 22.04, Windows 11, macOS Ventura]
- **Python Version:** [e.g., 3.10.12]
- **Browser:** [e.g., Chrome 120] (for UI issues)

### Logs/Screenshots
<!-- Paste relevant error logs or attach screenshots -->

### Additional Context
<!-- Any other information that might help -->
```
---

### Special Cases

#### 🤖 Model Hallucinations / Incorrect Mappings

> If the AI produces incorrect legal mappings:

```markdown
## 🤖 Incorrect Mapping Report

### Input
**IPC Section:** 420

### Expected Output
**BNS Section:** 318 (Cheating)

### Actual Output
<!-- What the system returned -->

### Source Reference
<!-- Link to official law document or gazette -->
```
---

#### 🖼️ OCR Accuracy Issues

```markdown
## 🖼️ OCR Issue Report

### Input Image
<!-- Attach the image that caused the issue -->

### Expected Text
<!-- What the image contains -->

### Extracted Text
<!-- What the OCR returned -->

### OCR Engine Used
- [ ] EasyOCR
- [ ] Pytesseract
```
---

### Beginner-Friendly Areas

New to the project? Here are some great places to start:

- 📚 **Documentation:** Improve README, add inline comments
- 🧪 **Testing:** Add unit tests for engine modules
- 🎨 **UI/UX:** Enhance Streamlit interface styling
- 📊 **Data:** Help expand IPC→BNS mapping coverage

Feel free to ask questions by opening a discussion or reaching out to maintainers!

---

<div align="center">

**Thank you for contributing to LexTransition-AI! 🚀**

*Together, we're making legal technology accessible to everyone.*

</div>