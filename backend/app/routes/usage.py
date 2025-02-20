from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from datetime import datetime, timedelta
import json
from ..dependencies import get_redis
from firebase_admin import auth
from ..utils.auth import get_current_user

router = APIRouter()

@router.get("/api/usage/stats")
async def get_usage_stats(
    current_user: dict = Depends(get_current_user),
    redis = Depends(get_redis)
):
    """Get usage statistics for the current user"""
    user_id = current_user["uid"]
    
    # Get total requests limit from Redis
    total_limit = await redis.get(f"user:{user_id}:total_limit")
    if total_limit is None:
        total_limit = 1000  # Default limit
        await redis.set(f"user:{user_id}:total_limit", total_limit)
    
    # Get current month's usage
    current_month = datetime.now().strftime("%Y-%m")
    monthly_usage = await redis.get(f"user:{user_id}:usage:{current_month}")
    monthly_usage = int(monthly_usage) if monthly_usage else 0
    
    # Get daily usage for the past 30 days
    daily_usage = []
    today = datetime.now()
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
    
    return {
        "total_limit": int(total_limit),
        "used_requests": monthly_usage,
        "remaining_requests": int(total_limit) - monthly_usage,
        "daily_usage": daily_usage
    }

@router.post("/api/usage/increment")
async def increment_usage(
    current_user: dict = Depends(get_current_user),
    redis = Depends(get_redis)
):
    """Increment usage counter for the current user"""
    user_id = current_user["uid"]
    today = datetime.now()
    
    # Increment daily counter
    daily_key = f"user:{user_id}:usage:{today.strftime('%Y-%m-%d')}"
    await redis.incr(daily_key)
    
    # Increment monthly counter
    monthly_key = f"user:{user_id}:usage:{today.strftime('%Y-%m')}"
    await redis.incr(monthly_key)
    
    return {"status": "success"}