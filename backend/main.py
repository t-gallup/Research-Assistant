from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import rag_pipeline as rp
import logging
import os
import uuid
import stripe
from fastapi.staticfiles import StaticFiles
import tts as t
from rate_limiter import rate_limiter
from firebase_auth import init_firebase, verify_firebase_token
from search_routes import router as search_router
from datetime import datetime
from cors_middleware import setup_cors, CustomCORSMiddleware

# Initialize Firebase
init_firebase()

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Price IDs for different tiers
PRICE_IDS = {
    'pro': os.getenv('STRIPE_PRO_PRICE_ID'),
    'plus': os.getenv('STRIPE_PLUS_PRICE_ID')
}

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Define request/response models
class URLInput(BaseModel):
    url: str

class UpgradeRequest(BaseModel):
    payment_method_id: str
    price_id: str

# Create FastAPI app
app = FastAPI()

# Set up CORS
app = setup_cors(app)

# Add custom CORS handling for extra reliability
app.add_middleware(CustomCORSMiddleware)

# Mount static files
app.mount("/audio", StaticFiles(directory="audio"), name="audio")

# Include routers
app.include_router(search_router)

# Create audio directory if it doesn't exist
os.makedirs("audio", exist_ok=True)


# Debug middleware to log requests
@app.middleware("http")
async def debug_middleware(request: Request, call_next):
    logger.debug(f"Incoming request: {request.method} {request.url}")
    logger.debug(f"Headers: {request.headers}")

    origin = request.headers.get("Origin", "")

    allowed_origins = [
        "https://main.d113ulshyf5fsx.amplifyapp.com",
        "https://main.d1g23bnvdsgbn1.amplifyapp.com",
        "https://research-assistant.app",
        "https://www.research-assistant.app"
    ]

    cors_origin = origin if origin in allowed_origins else None
    
    # Handle preflight OPTIONS requests immediately
    if request.method == "OPTIONS":
        logger.debug("Handling OPTIONS request")
        response = JSONResponse(content={"detail": "OK"})
        # Add CORS headers
        if cors_origin:
            response.headers["Access-Control-Allow-Origin"] = cors_origin
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept, Origin, X-Requested-With, X-Amz-Date, X-Api-Key, X-Amz-Security-Token"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Max-Age"] = "86400"
        return response
    
    # Process the request
    response = await call_next(request)
    
    # Add CORS headers to every response
    if cors_origin:
        response.headers["Access-Control-Allow-Origin"] = cors_origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    
    # Log response
    logger.debug(f"Response status: {response.status_code}")
    
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    return JSONResponse(content={"status": "healthy"})

# OPTIONS request handler for CORS preflight
@app.options("/{rest_of_path:path}")
async def options_handler(rest_of_path: str):
    return JSONResponse(content={"detail": "OK"})

# Rate limit endpoint
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

# Usage statistics endpoint
@app.get("/api/usage/stats")
async def get_usage_stats(request: Request,
                         token: dict = Depends(verify_firebase_token)):
    """Get usage statistics for the current user"""
    try:
        user_id = token.get('uid')
        logger.debug(f"Fetching usage stats for user: {user_id}")

        if request.method != "OPTIONS":
            # Get daily usage history
            daily_usage = await rate_limiter.get_daily_usage(user_id)
            
            # Get tier and limit info without incrementing
            tier = await rate_limiter.get_user_tier(user_id)
            limit = rate_limiter.rate_limit_tiers[tier]

            # Get current counts without incrementing
            today = datetime.now().strftime('%Y-%m-%d')
            requests_key = f"user:{user_id}:requests:{today}"
            current_requests = int(await rate_limiter.redis.get(requests_key) or 0)
            remaining = limit - current_requests
            
            response_data = {
                "total_limit": limit,
                "used_requests": current_requests,
                "remaining_requests": remaining,
                "daily_usage": daily_usage,
                "tier": tier
            }
            logger.debug(f"Returning usage stats: {response_data}")
            return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error in get_usage_stats: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Plan upgrade endpoint
@app.post("/api/upgrade")
async def upgrade_plan(
    upgrade_request: UpgradeRequest,
    request: Request,
    token: dict = Depends(verify_firebase_token)
):
    try:
        user_id = token.get('uid')

        # Validate the price_id
        if upgrade_request.price_id not in PRICE_IDS.values():
            raise HTTPException(status_code=400, detail="Invalid price ID")

        # Create or get customer
        customers = stripe.Customer.list(metadata={'firebase_uid': user_id})
        if customers.data:
            customer = customers.data[0]
        else:
            # Create new customer
            customer = stripe.Customer.create(
                metadata={'firebase_uid': user_id},
                payment_method=upgrade_request.payment_method_id,
                invoice_settings={
                    'default_payment_method': upgrade_request.payment_method_id
                }
            )

        # Create subscription
        try:
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{'price': upgrade_request.price_id}],
                payment_behavior='default_incomplete',
                payment_settings={'save_default_payment_method': 'on_subscription'},
                expand=['latest_invoice.payment_intent'],
                metadata={'firebase_uid': user_id}
            )

            # Update user's tier in rate limiter
            new_tier = 'pro' if upgrade_request.price_id == PRICE_IDS['pro'] else 'plus'
            await rate_limiter.set_user_tier(user_id, new_tier)
            
            return {
                'subscription_id': subscription.id,
                'client_secret': subscription.latest_invoice.payment_intent.client_secret,
                'status': subscription.status
            }

        except stripe.error.CardError as e:
            raise HTTPException(status_code=400, detail=str(e.error))
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error upgrading plan: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Stripe webhook endpoint
@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    try:
        # Get the webhook secret from environment variables
        webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        
        # Get the stripe signature from headers
        stripe_signature = request.headers.get('stripe-signature')
        
        # Get the raw request body
        payload = await request.body()
        
        try:
            # Verify the event
            event = stripe.Webhook.construct_event(
                payload, stripe_signature, webhook_secret
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            raise HTTPException(status_code=400, detail="Invalid signature")

        # Handle the event
        if event.type == 'customer.subscription.updated':
            subscription = event.data.object
            user_id = subscription.metadata.get('firebase_uid')
            
            if user_id:
                # Update user's tier based on subscription status
                if subscription.status == 'active':
                    # Determine tier from price ID
                    if subscription.items.data[0].price.id == PRICE_IDS['pro']:
                        await rate_limiter.set_user_tier(user_id, 'pro')
                    elif subscription.items.data[0].price.id == PRICE_IDS['plus']:
                        await rate_limiter.set_user_tier(user_id, 'plus')
                elif subscription.status in ['incomplete_expired', 'canceled']:
                    # Reset to free tier
                    await rate_limiter.set_user_tier(user_id, 'free')
                    
        elif event.type == 'customer.subscription.deleted':
            subscription = event.data.object
            user_id = subscription.metadata.get('firebase_uid')
            
            if user_id:
                # Reset to free tier
                await rate_limiter.set_user_tier(user_id, 'free')

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# QnA generation endpoint
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

# Audio generation endpoint
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

# Shutdown event handler
@app.on_event("shutdown")
async def shutdown_event():
    await rate_limiter.close()