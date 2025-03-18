from mangum import Mangum
import os

# Set environment variables before importing the app
os.environ['ENVIRONMENT'] = 'production'

# Import the FastAPI app
from main import app

# Create the handler
handler = Mangum(app)
