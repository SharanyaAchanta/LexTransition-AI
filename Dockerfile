# 1. Lightweight Python 3.10
FROM python:3.10-slim

# 2. Install System Dependencies (Added wget and libsndfile1 for TTS)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    libsqlite3-dev \
    curl \
    wget \
    libsndfile1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 3. Set Working Directory
WORKDIR /app

# 4. Copy Requirements & Install Dependencies
COPY requirements.txt .
# Using --no-cache-dir for lower disk usage
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# 5. Pre-fetch TTS Models (Baking the models into the image)
RUN mkdir -p models/tts temp_audio && \
    wget -q -O models/tts/en_US-lessac-medium.onnx \
    https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx && \
    wget -q -O models/tts/en_US-lessac-medium.onnx.json \
    https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json && \
    chmod 777 temp_audio

# 6. Copy the Application Code
COPY . .

# 7. Final Folder Prep
RUN mkdir -p law_pdfs vector_store

# 8. Expose Streamlit Port
EXPOSE 8501

# 9. Healthcheck 
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# 10. Start the App
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]