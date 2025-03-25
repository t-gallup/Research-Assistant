import os
import logging
from mangum import Mangum

# Set environment variables before importing the app
os.environ['ENVIRONMENT'] = os.environ.get('ENVIRONMENT', 'production')
os.environ['DEPLOYMENT'] = os.environ.get('DEPLOYMENT', 'aws')

# Import the app at module level
from main import app

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the mangum handler at module level
handler = Mangum(app,
                lifespan="off",
                api_gateway_base_path=None)
