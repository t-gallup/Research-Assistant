import os
import logging
from mangum import Mangum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set environment variables before importing the app
os.environ['ENVIRONMENT'] = 'production'
os.environ['DEPLOYMENT'] = 'aws'

try:
    # Import the app only after setting the environment
    from main import app
    
    # Create the lambda handler with lifespan turned off for containerized Lambda
    handler = Mangum(app,
                     lifespan="off",
                     api_gateway_base_path=None)
    
    logger.info("Lambda handler initialized successfully")

except Exception as e:
    logger.error(f"Error initializing handler: {str(e)}")
    raise
