FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# Install Python, pip and FFmpeg
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create audio directory
RUN mkdir audio

# Copy backend files
COPY config.py .
COPY firebase_auth.py .
COPY requirements.txt .
COPY main.py .
COPY rag_pipeline.py .
COPY rate_limiter.py .
COPY search_routes.py .
COPY summarize_script.py .
COPY tts.py .
COPY firebase-adminsdk.json .

# Install requirements
RUN pip3 install -r requirements.txt

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the FastAPI app
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 