import os
import logging
import json
import traceback
from mangum import Mangum

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def handler(event, context):
    """
    Enhanced Lambda handler with detailed logging for debugging API Gateway integration issues
    """
    try:
        # Log environment information
        logger.debug(f"Lambda execution environment: {os.environ.get('DEPLOYMENT', 'unknown')}")
        logger.debug(f"Event: {json.dumps(event)}")
        
        if context:
            logger.debug(f"Lambda function ARN: {context.invoked_function_arn}")
            logger.debug(f"Lambda function memory: {context.memory_limit_in_mb}MB")
            logger.debug(f"Lambda function remaining time: {context.get_remaining_time_in_millis()}ms")
        
        # Set environment variables before importing the app
        os.environ['ENVIRONMENT'] = os.environ.get('ENVIRONMENT', 'production')
        os.environ['DEPLOYMENT'] = os.environ.get('DEPLOYMENT', 'aws')
        
        try:
            # Import the app only after setting the environment
            from main import app
            logger.debug("Successfully imported FastAPI app from main.py")
            
            # Create the mangum handler with lifespan turned off for containerized Lambda
            mangum_handler = Mangum(app,
                               lifespan="off",
                               api_gateway_base_path=None)
            logger.debug("Created Mangum handler")
            
            # Execute the handler and capture the response
            response = mangum_handler(event, context)
            
            # Log the complete response
            if isinstance(response, dict):
                # Truncate body if it's too large
                if 'body' in response and isinstance(response['body'], str) and len(response['body']) > 1000:
                    log_response = response.copy()
                    log_response['body'] = f"{response['body'][:1000]}... [truncated]"
                    logger.debug(f"Lambda response (truncated): {json.dumps(log_response)}")
                else:
                    logger.debug(f"Lambda response: {json.dumps(response)}")
            else:
                logger.debug(f"Lambda response (non-JSON): {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error importing app or creating handler: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    except Exception as e:
        logger.error(f"Unhandled exception in Lambda handler: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Return a properly formatted error response for API Gateway
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With"
            },
            "body": json.dumps({
                "error": "Internal server error",
                "message": str(e),
                "trace_id": context.aws_request_id if context else None
            })
        }