from fastapi import Request, HTTPException
from redis.asyncio import Redis
from datetime import datetime, timedelta
import os


class RateLimiter:
    def __init__(self):
        redis_host = 'localhost' if os.getenv('ENVIRONMENT') != 'production' else os.getenv('REDIS_HOST')

        self.redis = Redis(
            host=redis_host,
            port=int(os.getenv('REDIS_PORT', 6379)),
            username=os.getenv('REDIS_USERNAME'),
            password=os.getenv('REDIS_PASSWORD'),
            db=0,
            decode_responses=True
        )
        
        # Define rate limit tiers (requests per day)
        self.rate_limit_tiers = {
            'free': 50,
            'basic': 200,
            'premium': 1000
        }

    async def get_user_tier(self, user_id: str) -> str:
        """Get the user's subscription tier."""
        tier = await self.redis.get(f"user:{user_id}:tier")
        return tier if tier else 'free'

    async def get_remaining_requests(self, user_id: str) -> int:
        """Get remaining requests for the user."""
        today = datetime.now().strftime('%Y-%m-%d')
        requests_key = f"user:{user_id}:requests:{today}"
        
        # Get current request count
        current_requests = int(await self.redis.get(requests_key) or 0)
        
        # Get user's tier and max requests
        tier = await self.get_user_tier(user_id)
        max_requests = self.rate_limit_tiers[tier]
        
        return max_requests - current_requests

    async def check_rate_limit(self, request: Request, token: dict):
        """Middleware to check rate limits."""
        user_id = token.get('uid')
        
        today = datetime.now().strftime('%Y-%m-%d')
        requests_key = f"user:{user_id}:requests:{today}"
        
        # Get current request count
        current_requests = int(await self.redis.get(requests_key) or 0)
        
        # Get user's tier and max requests
        tier = await self.get_user_tier(user_id)
        max_requests = self.rate_limit_tiers[tier]
        
        if current_requests >= max_requests:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "tier": tier,
                    "limit": max_requests,
                    "reset": "next day"
                }
            )
        
        # Increment request count
        await self.redis.incr(requests_key)
        
        # Set expiry for request counter (48 hours to be safe)
        await self.redis.expire(requests_key, 60 * 60 * 48)

    async def set_user_tier(self, user_id: str, tier: str):
        """Set a user's subscription tier."""
        if tier not in self.rate_limit_tiers:
            raise ValueError(f"Invalid tier. Must be one of: {list(self.rate_limit_tiers.keys())}")
        
        await self.redis.set(f"user:{user_id}:tier", tier)

    async def close(self):
        """Close Redis connection."""
        await self.redis.close()

# Initialize rate limiter
rate_limiter = RateLimiter()