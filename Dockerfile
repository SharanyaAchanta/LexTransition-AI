# 1. Base Image: Lightweight Python 3.10
FROM python:3.10-slim

# 2. Install System Dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 3. Set Working Directory
WORKDIR /app

# 4. Copy Requirements & Install Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# 5. Copy the Application Code
COPY . .

# 6. Create Storage Folders
RUN mkdir -p law_pdfs vector_store

# 7. Expose Streamlit Port
EXPOSE 8501

# 8. Add Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# 9. Start the App
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]