from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response
import os
import logging

logger = logging.getLogger(__name__)

def setup_cors(app):
    """Set up CORS middleware with appropriate settings"""
    # Get allowed origins from environment or use defaults
    amplify_url = os.getenv('AMPLIFY_URL', 'https://main.d113ulshyf5fsx.amplifyapp.com')
    logger.info(f"Setting up CORS with Amplify URL: {amplify_url}")
    
    # Define allowed origins
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://research-assistant.app",
        "https://www.research-assistant.app",
        amplify_url,
        "https://main.d113ulshyf5fsx.amplifyapp.com"
    ]
    
    # Add the CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_origin_regex=None,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=86400,
    )
    
    # Log CORS settings
    logger.info(f"CORS middleware added with {len(origins)} origins")
    return app

class CustomCORSMiddleware:
    """Additional middleware to handle CORS for tricky cases"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if this is an OPTIONS request (preflight)
        is_options = False
        if scope["method"] == "OPTIONS":
            is_options = True
            
        async def send_wrapper(message):
            """Wrap the send function to add CORS headers to all responses"""
            if message["type"] == "http.response.start":
                # Start of response, add CORS headers
                headers = dict(message.get("headers", []))
                
                # Add CORS headers
                headers[b"access-control-allow-origin"] = b"*"
                headers[b"access-control-allow-methods"] = b"GET, POST, PUT, DELETE, OPTIONS"
                headers[b"access-control-allow-headers"] = b"Content-Type, Authorization, X-Requested-With, Accept"
                headers[b"access-control-allow-credentials"] = b"true"
                headers[b"access-control-max-age"] = b"86400"  # 24 hours
                
                # Convert headers back to list of tuples
                message["headers"] = [(k, v) for k, v in headers.items()]
                
            await send(message)
        
        # If this is an OPTIONS request, respond immediately with 200 OK
        if is_options:
            async def receive_wrapper():
                message = await receive()
                return message
                
            # Send a 200 OK response with CORS headers for OPTIONS requests
            await send({
                "type": "http.response.start",
                "status": 200,
                "headers": [
                    (b"content-length", b"0"),
                    (b"access-control-allow-origin", b"*"),
                    (b"access-control-allow-methods", b"GET, POST, PUT, DELETE, OPTIONS"),
                    (b"access-control-allow-headers", b"Content-Type, Authorization, X-Requested-With, Accept"),
                    (b"access-control-allow-credentials", b"true"),
                    (b"access-control-max-age", b"86400"),
                ],
            })
            await send({"type": "http.response.body", "body": b""})
            return
            
        # Pass the request to the app with our wrapped send function
        await self.app(scope, receive, send_wrapper)
