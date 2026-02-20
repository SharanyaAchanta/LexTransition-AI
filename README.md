# LexTransition-AI

LexTransition-AI is a Streamlit-based legal assistant focused on helping users map legacy Indian law references (IPC/CrPC/IEA) to updated law frameworks (BNS/BNSS/BSA), analyze documents with OCR, and perform grounded law-PDF lookups.

Live demo: https://kvbgkvw4mehwhhdjt7crrg.streamlit.app/

## What this project includes

- Section mapping workflow (IPC to BNS and related acts)
- OCR utilities for image-based legal content
- Grounded PDF lookup and retrieval helpers
- Streamlit UI for interactive use
- Automated test coverage for core engine modules

## Repository structure

```text
LexTransition-AI/
├── app.py
├── cli.py
├── engine/
├── tests/
├── assets/
├── law_pdfs/
├── vector_store/
├── requirements.txt
├── Dockerfile
└── docker-compose.yaml
```

## Technology stack

- Python 3.10 (standardized for local, Docker, and CI)
- Streamlit UI
- PDF and OCR processing libraries (see `requirements.txt`)
- Pytest for tests
- GitHub Actions for CI

## Prerequisites

- Python 3.10
- `pip` (latest recommended)
- Optional: Docker / Docker Compose

## Local setup

1. Clone the repository:

   ```bash
   git clone https://github.com/centiceron/LexTransition-AI.git
   cd LexTransition-AI
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   # Windows PowerShell
   .\.venv\Scripts\Activate.ps1
   # macOS/Linux
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Run the app:

   ```bash
   streamlit run app.py
   ```

5. Open:

   ```text
   http://localhost:8501
   ```

## Running tests locally

```bash
pytest -q
```

## Docker deployment

### Build and run with Docker

```bash
docker build -t lextransition-ai .
docker run --rm -p 8501:8501 lextransition-ai
```

### Run with Docker Compose

```bash
docker compose up --build
```

The container exposes the Streamlit application on port `8501`.

## CI/CD pipeline

The GitHub Actions workflow is defined in `.github/workflows/lextransition-ci.yml` and runs on:

- Pushes to `main`
- All pull requests

Pipeline stages:

1. Checkout source code
2. Set up Python 3.10 with pip cache
3. Install required system packages (`libsndfile1`, `ffmpeg`)
4. Install Python dependencies and run dependency validation (`pip check`)
5. Run lint checks (`ruff` critical checks)
6. Run automated tests (`pytest -q`)

This ensures each PR is validated for dependency integrity, syntax-level lint quality, and test stability before merge.

## Deployment guidance

For production-style deployments:

- Prefer Docker-based runtime for environment consistency.
- Pin deployment runtime to Python 3.10 to match CI and local setup.
- Store large models/data outside the image when possible and mount volumes.
- Use CI as the merge gate so only passing commits are deployed.

## Current implementation status

- Streamlit UI: implemented
- Mapping logic and persistence: implemented
- OCR support: implemented (engine-dependent)
- Grounded PDF lookup: implemented
- Advanced embedding/LLM paths: partially implemented / optional

## Contributing

- Open an issue describing the problem or enhancement.
- Submit a pull request with focused changes and tests where applicable.
- Ensure CI passes before requesting review.

See `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` for contribution standards.