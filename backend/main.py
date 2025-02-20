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

# Configure CORS with specific origins
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
        remaining = rate_limiter.get_remaining_requests(user_id)
        tier = rate_limiter.get_user_tier(user_id)
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
        remaining = rate_limiter.get_remaining_requests(user_id)
        tier = rate_limiter.get_user_tier(user_id)
        limit = rate_limiter.rate_limit_tiers[tier]
        used = limit - remaining

        # Get daily usage for the past 30 days from Redis
        daily_usage = []
        today = datetime.now()
        redis = rate_limiter.redis  # Access Redis from rate_limiter
        
        for i in range(30):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            count = await redis.get(f"user:{user_id}:usage:{date}")
            if count:
                daily_usage.append({
                    "date": date,
                    "requests": int(count)
                })
        
        # Sort by date ascending
        daily_usage.sort(key=lambda x: x["date"])
        
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
        logger.error(f"Error in get_usage_stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Rest of your routes remain the same...