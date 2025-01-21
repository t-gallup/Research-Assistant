from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
import torch

app = FastAPI()

# Model initialization
summarizer = None

class SummarizationRequest(BaseModel):
    text: str
    max_length: int = 130
    min_length: int = 30

@app.on_event("startup")
async def load_model():
    global summarizer
    # Check for GPU
    device = 0 if torch.cuda.is_available() else -1
    summarizer = pipeline(
        "summarization",
        model="facebook/bart-large-cnn",
        device=device
    )

@app.post("/summarize")
async def summarize(request: SummarizationRequest):
    try:
        summary = summarizer(
            request.text,
            max_length=request.max_length,
            min_length=request.min_length,
            do_sample=False
        )
        return {"summary": summary[0]["summary_text"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}