from fastapi import Request, HTTPException
from redis.asyncio import Redis
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        # Set up more detailed logging
        logger.setLevel(logging.DEBUG)
        
        # Get Redis connection parameters from environment
        redis_host = 'localhost' if os.getenv('ENVIRONMENT') != 'production' else os.getenv('REDIS_HOST')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        redis_user = os.getenv('REDIS_USERNAME', '')
        redis_password = os.getenv('REDIS_PASSWORD', '')
        
        logger.debug(f"Connecting to Redis at {redis_host}:{redis_port} (User: {redis_user})")
        
        try:
            self.redis = Redis(
                host=redis_host,
                port=redis_port,
                username=redis_user,
                password=redis_password,
                db=0,
                decode_responses=True
            )
            logger.debug("Redis connection initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Redis connection: {str(e)}")
            # Create a dummy implementation for development/testing
            self.redis = None
            
        # Define rate limit tiers (requests per day)
        self.rate_limit_tiers = {
            'free': 50,
            'basic': 200,
            'premium': 1000
        }

    async def get_user_tier(self, user_id: str) -> str:
        """Get the user's subscription tier."""
        if not self.redis:
            logger.warning("Redis not available, returning default tier")
            return 'free'
            
        try:
            tier = await self.redis.get(f"user:{user_id}:tier")
            logger.debug(f"User {user_id} tier: {tier or 'free (default)'}")
            return tier if tier else 'free'
        except Exception as e:
            logger.error(f"Error getting user tier: {str(e)}")
            return 'free'

    async def get_remaining_requests(self, user_id: str) -> int:
        """Get remaining requests for the user."""
        if not self.redis:
            logger.warning("Redis not available, returning default limit")
            return self.rate_limit_tiers['free']
            
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            requests_key = f"user:{user_id}:requests:{today}"
            
            # Get current request count
            current_requests = int(await self.redis.get(requests_key) or 0)
            
            # Get user's tier and max requests
            tier = await self.get_user_tier(user_id)
            max_requests = self.rate_limit_tiers.get(tier, self.rate_limit_tiers['free'])
            
            remaining = max_requests - current_requests
            logger.debug(f"User {user_id} remaining requests: {remaining} (used: {current_requests}, max: {max_requests})")
            return remaining
        except Exception as e:
            logger.error(f"Error getting remaining requests: {str(e)}")
            return self.rate_limit_tiers['free']

    async def check_rate_limit(self, request: Request, token: dict, is_internal: bool = False):
        """Middleware to check rate limits."""
        if not self.redis:
            logger.warning("Redis not available, skipping rate limit check")
            return
            
        # Log the request details
        logger.debug(f"Rate limit check - Method: {request.method}, URL: {request.url.path}, Internal: {is_internal}")
        
        # Skip rate limiting for OPTIONS requests and internal API calls
        if request.method == "OPTIONS" or is_internal:
            logger.debug("Skipping rate limit check (OPTIONS or internal request)")
            return
            
        try:
            user_id = token.get('uid')
            if not user_id:
                logger.error("Missing user ID in token")
                raise HTTPException(status_code=401, detail="Invalid authentication token")
                
            today = datetime.now().strftime('%Y-%m-%d')
            requests_key = f"user:{user_id}:requests:{today}"
            usage_key = f"user:{user_id}:usage:{today}"

            # Get current request count
            current_requests = int(await self.redis.get(requests_key) or 0)
            logger.debug(f"Current request count for user {user_id}: {current_requests}")
            
            # Get user's tier and max requests
            tier = await self.get_user_tier(user_id)
            max_requests = self.rate_limit_tiers.get(tier, self.rate_limit_tiers['free'])
            
            if current_requests >= max_requests:
                logger.warning(f"Rate limit exceeded for user {user_id}")
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded",
                        "tier": tier,
                        "limit": max_requests,
                        "reset": "next day"
                    }
                )
            
            # Increment request count and daily usage
            await self.redis.incr(requests_key)
            await self.redis.incr(usage_key)
            logger.debug(f"Incremented request count for user {user_id} - New count: {current_requests + 1}")
            
            # Set expiry for counters (48 hours to be safe)
            await self.redis.expire(requests_key, 60 * 60 * 48)
            await self.redis.expire(usage_key, 60 * 60 * 48)
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Error in check_rate_limit: {str(e)}")
            # Don't block the request if Redis is down
            return

    async def get_daily_usage(self, user_id: str, days: int = 30) -> list:
        """Get daily usage for the past N days."""
        if not self.redis:
            logger.warning("Redis not available, returning empty usage data")
            return []
            
        try:
            daily_usage = []
            today = datetime.now()
            
            for i in range(days):
                date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
                usage_key = f"user:{user_id}:usage:{date}"
                count = await self.redis.get(usage_key)
                if count:
                    daily_usage.append({
                        "date": date,
                        "requests": int(count)
                    })
            
            logger.debug(f"Retrieved {len(daily_usage)} days of usage data for user {user_id}")
            return sorted(daily_usage, key=lambda x: x["date"])
        except Exception as e:
            logger.error(f"Error getting daily usage: {str(e)}")
            return []

    async def set_user_tier(self, user_id: str, tier: str):
        """Set a user's subscription tier."""
        if not self.redis:
            logger.warning(f"Redis not available, cannot set tier for user {user_id}")
            return
            
        try:
            if tier not in self.rate_limit_tiers:
                logger.error(f"Invalid tier '{tier}' for user {user_id}")
                raise ValueError(f"Invalid tier. Must be one of: {list(self.rate_limit_tiers.keys())}")
            
            await self.redis.set(f"user:{user_id}:tier", tier)
            logger.info(f"Set user {user_id} tier to {tier}")
        except Exception as e:
            logger.error(f"Error setting user tier: {str(e)}")
            raise

    async def close(self):
        """Close Redis connection."""
        if self.redis:
            try:
                await self.redis.close()
                logger.debug("Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {str(e)}")

# Initialize rate limiter
rate_limiter = RateLimiter()