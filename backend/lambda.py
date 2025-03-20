import os
from mangum import Mangum

# Set environment variables before importing the app
os.environ['ENVIRONMENT'] = 'production'

# Import the app only after setting the environment
from main import app

# Create the lambda handler
handler = Mangum(app, lifespan="off")
