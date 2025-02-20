from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
from search_routes import router as search_router
from datetime import datetime, timedelta

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
origins = [
    "http://localhost:3000",  # React development server
    "http://localhost:5173",  # Vite development server
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/audio", StaticFiles(directory="audio"), name="audio")

app.include_router(search_router)

os.makedirs("audio", exist_ok=True)


@app.middleware("http")
async def debug_middleware(request: Request, call_next):
    logger.debug(f"Incoming request: {request.method} {request.url}")
    logger.debug("Auth header: %s", request.headers.get("Authorization"))
    response = await call_next(request)
    return response


@app.get("/health")
async def health_check():
    return JSONResponse(content={"status": "healthy"})


@app.get("/api/rate-limit")
async def get_rate_limit(request: Request,
                         token: dict = Depends(verify_firebase_token)
                         ):
    try:
        user_id = token.get('uid')
        remaining = await rate_limiter.get_remaining_requests(user_id)
        tier = await rate_limiter.get_user_tier(user_id)
        limit = rate_limiter.rate_limit_tiers[tier]
        
        return JSONResponse(content={
            "tier": tier,
            "limit": limit,
            "remaining": remaining,
            "reset": "next day"
        })
    except Exception as e:
        logger.error(f"Error in get_rate_limit: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/usage/stats")
async def get_usage_stats(request: Request,
                         token: dict = Depends(verify_firebase_token)):
    """Get usage statistics for the current user"""
    try:
        user_id = token.get('uid')
        logger.debug(f"Fetching usage stats for user: {user_id}")
        
        # Get usage data from rate limiter
        remaining = await rate_limiter.get_remaining_requests(user_id)
        tier = await rate_limiter.get_user_tier(user_id)
        limit = rate_limiter.rate_limit_tiers[tier]
        used = limit - remaining

        # Get daily usage history
        daily_usage = await rate_limiter.get_daily_usage(user_id)
        
        response_data = {
            "total_limit": limit,
            "used_requests": used,
            "remaining_requests": remaining,
            "daily_usage": daily_usage,
            "tier": tier
        }
        logger.debug(f"Returning usage stats: {response_data}")
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error in get_usage_stats: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


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

        # Generate audio asynchronously without counting it as a separate request
        try:
            audio_request = Request(scope={"type": "http"})
            audio_result = await generate_audio(url_input, audio_request, token, is_internal=True)
            has_audio = True
            audio_data = audio_result
        except Exception as e:
            logger.error(f"Error generating audio: {str(e)}")
            has_audio = False
            audio_data = None

        return JSONResponse(content={
            "articleTitle": article_title,
            "summary": initial_summary,
            "qnaPairs": [{"question": q, "answer": a} for q,
                         a in zip(questions, answers)],
            "recommendedArticles": [{"title": t, "link": l} for t,
                                    l in zip(rec_titles, rec_links)],
            "audio": audio_data if has_audio else None
        })
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-audio")
async def generate_audio(url_input: URLInput,
                         request: Request,
                         token: dict = Depends(verify_firebase_token),
                         is_internal: bool = False
                         ):
    # Check rate limit only if not an internal request
    if not is_internal:
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


@app.on_event("shutdown")
async def shutdown_event():
    await rate_limiter.close()