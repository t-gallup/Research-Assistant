from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import rag_pipeline as rp
import logging
import os
import uuid
from fastapi.staticfiles import StaticFiles
import tts as t
from rate_limiter import rate_limiter
from config import load_secrets
from firebase_auth import init_firebase, verify_firebase_token

load_secrets()

init_firebase()

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class URLInput(BaseModel):
    url: str


app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/audio", StaticFiles(directory="audio"), name="audio")

os.makedirs("audio", exist_ok=True)


@app.middleware("http")
async def debug_middleware(request: Request, call_next):
    print("Auth header:", request.headers.get("Authorization"))
    response = await call_next(request)
    return response


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/rate-limit")
async def get_rate_limit(request: Request,
                         token: dict = Depends(verify_firebase_token)
                         ):
    user_id = token.get('uid')
    remaining = rate_limiter.get_remaining_requests(user_id)
    tier = rate_limiter.get_user_tier(user_id)
    limit = rate_limiter.rate_limit_tiers[tier]
    
    return {
        "tier": tier,
        "limit": limit,
        "remaining": remaining,
        "reset": "next day"
    }


@app.post("/api/generate-qna")
async def generate_qna(url_input: URLInput,
                       request: Request,
                       token: dict = Depends(verify_firebase_token)
                       ):
    # Check rate limit
    await rate_limiter.check_rate_limit(request, token)
    
    try:
        logger.info(f"Processing URL: {url_input}")

        # Get initial summary using Gemini
        initial_summary, article_title = rp.summarize_content(url_input.url)
        logger.info("Initial summary generated")

        topic_list = rp.prompt_llm_for_related_topics(initial_summary)
        questions, answers = rp.prompt_llm(initial_summary)
        logger.info("Q&A generated")

        # Get recommended articles
        rec_titles, rec_links = [], []
        for topic in topic_list[:min(2, len(topic_list))]:
            results = rp.search_google(topic)
            new_rec_titles, new_rec_links = \
                rp.get_top_5_articles(results, url_input.url)
            rec_titles.extend(new_rec_titles)
            rec_links.extend(new_rec_links)

        logger.info("Recommended articles retrieved")

        return {
            "articleTitle": article_title,
            "summary": initial_summary,
            "qnaPairs": [{"question": q, "answer": a} for q,
                         a in zip(questions, answers)],
            "recommendedArticles": [{"title": t, "link": l} for t,
                                    l in zip(rec_titles, rec_links)]
        }
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-audio")
async def generate_audio(url_input: URLInput,
                         request: Request,
                         token: dict = Depends(verify_firebase_token)
                         ):
    # Check rate limit
    await rate_limiter.check_rate_limit(request, token)
    
    try:
        summarizer = t.PDFAudioSummarizer(
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            azure_key=os.getenv('AZURE_SPEECH_KEY'),
            azure_region="westus2"
        )
        output_file = f"audio/audio_{uuid.uuid4()}.mp3"
        result = summarizer.process_file(url_input.url, output_file)
        
        if result["success"]:
            return {
                "status": "success",
                "audio_file": os.path.basename(output_file),
                "chunk_summaries": result["chunk_summaries"]
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to process file")

    except Exception as e:
        logger.error(f"Error generating audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))