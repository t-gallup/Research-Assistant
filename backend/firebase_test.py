import os
import json
import logging
import traceback
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

class TestResponse(BaseModel):
    status: str
    message: str
    details: dict = {}

@router.get("/api/test-firebase", response_model=TestResponse)
async def test_firebase():
    """Test endpoint to verify Firebase configuration"""
    try:
        # Get working directory and contents
        cwd = os.getcwd()
        dir_contents = os.listdir(cwd)
        
        # Check for Firebase credentials file
        cred_path = os.path.join(cwd, 'firebase-adminsdk.json')
        file_exists = os.path.exists(cred_path)
        file_size = os.path.getsize(cred_path) if file_exists else 0
        file_readable = os.access(cred_path, os.R_OK) if file_exists else False
        
        # Try to read the file if it exists
        file_content_sample = None
        file_json_valid = False
        file_structure = {}
        
        if file_exists and file_readable:
            try:
                with open(cred_path, 'r') as f:
                    # Read only first 20 characters to avoid logging sensitive data
                    file_content_sample = f.read(20) + "..." 
                    
                    # Reset file pointer and try to parse as JSON
                    f.seek(0)
                    try:
                        creds_json = json.load(f)
                        file_json_valid = True
                        
                        # Extract non-sensitive information
                        if "project_id" in creds_json:
                            file_structure["project_id"] = creds_json["project_id"]
                        
                        if "type" in creds_json:
                            file_structure["type"] = creds_json["type"]
                            
                        if "client_email" in creds_json:
                            email = creds_json["client_email"]
                            file_structure["client_email"] = email.split("@")[0] + "@..."
                    except json.JSONDecodeError:
                        file_json_valid = False
            except Exception as e:
                logger.error(f"Error reading credentials file: {str(e)}")
        
        # Check environment variables
        env_vars = {
            "FIREBASE_PROJECT_ID": os.getenv("FIREBASE_PROJECT_ID", "Not set"),
            "DEPLOYMENT": os.getenv("DEPLOYMENT", "Not set"),
            "ENVIRONMENT": os.getenv("ENVIRONMENT", "Not set")
        }
        
        details = {
            "working_directory": cwd,
            "directory_contents": dir_contents,
            "credential_file": {
                "path": cred_path,
                "exists": file_exists,
                "size_bytes": file_size,
                "readable": file_readable,
                "content_sample": file_content_sample if file_content_sample else "N/A",
                "valid_json": file_json_valid,
                "structure": file_structure
            },
            "environment_variables": env_vars
        }
        
        # Try to initialize Firebase
        try:
            from firebase_admin import credentials, initialize_app, get_app
            
            # Check if already initialized
            try:
                app = get_app()
                firebase_initialized = True
                firebase_status = "Already initialized"
            except:
                # Try to initialize
                if file_exists and file_json_valid:
                    cred = credentials.Certificate(cred_path)
                    initialize_app(cred, {
                        'projectId': env_vars["FIREBASE_PROJECT_ID"]
                    })
                    firebase_initialized = True
                    firebase_status = "Successfully initialized"
                else:
                    firebase_initialized = False
                    firebase_status = "Failed to initialize - invalid credentials"
        except Exception as e:
            firebase_initialized = False
            firebase_status = f"Error: {str(e)}"
            logger.error(traceback.format_exc())
        
        details["firebase_test"] = {
            "initialized": firebase_initialized,
            "status": firebase_status
        }
        
        return TestResponse(
            status="success" if firebase_initialized else "error",
            message="Firebase test completed",
            details=details
        )
        
    except Exception as e:
        logger.error(f"Error in test-firebase endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return TestResponse(
            status="error",
            message=f"Test failed: {str(e)}",
            details={"error": traceback.format_exc()}
        )
