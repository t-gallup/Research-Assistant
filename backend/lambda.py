from mangum import Mangum
import os
from main import app

# Set environment variables before importing the app
os.environ['ENVIRONMENT'] = 'production'

# Create the handler
handler = Mangum(app)
