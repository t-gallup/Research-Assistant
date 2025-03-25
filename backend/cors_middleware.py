from fastapi.middleware.cors import CORSMiddleware
import logging

logger = logging.getLogger(__name__)

def setup_cors(app):
    """Set up CORS middleware with appropriate settings"""
    # Define allowed origins
    origins = [
        "https://research-assistant.app",
        "https://www.research-assistant.app",
        "https://main.d1g23bnvdsgbn1.amplifyapp.com",
        "https://main.d113ulshyf5fsx.amplifyapp.com"
    ]
    
    # Add the CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_origin_regex=None,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With",
                       "X-Amz-Date", "X-Api-Key", "X-Amz-Security-Token"],
        expose_headers=["Content-Type", "Content-Length"],
        max_age=86400,
    )
    
    # Log CORS settings
    logger.info(f"CORS middleware added with {len(origins)} origins")
    return app

class CustomCORSMiddleware:
    """Additional middleware to handle CORS for tricky cases"""
    
    def __init__(self, app):
        self.app = app

        self.allowed_origins = [
            "https://research-assistant.app",
            "https://www.research-assistant.app",
            "https://main.d1g23bnvdsgbn1.amplifyapp.com",
            "https://main.d113ulshyf5fsx.amplifyapp.com"
        ]
        self.logger = logging.getLogger(__name__)
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Extract origin from headers
        origin = None
        for header_name, header_value in scope.get("headers", []):
            if header_name == b"origin":
                origin = header_value.decode("utf-8")
                break
        
        self.logger.debug(f"Origin header: {origin}")
        
        # Check if origin is allowed
        cors_origin = origin if origin in self.allowed_origins else None
        
        # Check if this is an OPTIONS request (preflight)
        is_options = False
        if scope["method"] == "OPTIONS":
            is_options = True
            
        async def send_wrapper(message):
            """Wrap the send function to add CORS headers to all responses"""
            if message["type"] == "http.response.start":
                # Start of response, add CORS headers
                headers = dict(message.get("headers", []))
                
                # Add CORS headers with specific origin
                if cors_origin:
                    headers[b"access-control-allow-origin"] = cors_origin.encode("utf-8")
                    headers[b"access-control-allow-methods"] = b"GET, POST, PUT, DELETE, OPTIONS"
                    headers[b"access-control-allow-headers"] = b"Content-Type, Authorization, X-Requested-With, Accept, Origin, X-Amz-Date, X-Api-Key, X-Amz-Security-Token"
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
            cors_headers = []
            if cors_origin:
                cors_headers = [
                    (b"content-length", b"0"),
                    (b"access-control-allow-origin", cors_origin.encode("utf-8")),
                    (b"access-control-allow-methods", b"GET, POST, PUT, DELETE, OPTIONS"),
                    (b"access-control-allow-headers", b"Content-Type, Authorization, X-Requested-With, Accept, Origin, X-Amz-Date, X-Api-Key, X-Amz-Security-Token"),
                    (b"access-control-allow-credentials", b"true"),
                    (b"access-control-max-age", b"86400"),
                ]
            else:
                cors_headers = [
                    (b"content-length", b"0")
                ]
                
            await send({
                "type": "http.response.start",
                "status": 200,
                "headers": cors_headers,
            })
            await send({"type": "http.response.body", "body": b""})
            return

        # Pass the request to the app with our wrapped send function
        await self.app(scope, receive, send_wrapper)
