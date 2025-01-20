FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# Install Python, pip and FFmpeg
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy all application files
COPY requirements.txt .
COPY main.py .
COPY rag_pipeline.py .

# Install requirements
RUN pip3 install -r requirements.txt

# Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]