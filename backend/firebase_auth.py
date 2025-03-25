import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Request
import os
import logging
import traceback
import json

# Set up logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def init_firebase():
    try:
        # Try to load from credentials file
        cred_path = os.path.join(os.path.dirname(__file__), 'firebase-adminsdk.json')
        logger.info(f"Initializing Firebase with credentials file: {cred_path}")
        
        # Check if file exists
        if not os.path.exists(cred_path):
            logger.error(f"Firebase credentials file not found at {cred_path}")
            
            # Check directory contents
            dir_path = os.path.dirname(__file__)
            logger.error(f"Directory contents of {dir_path}: {os.listdir(dir_path)}")
            
            # Try alternative approach - use environment variable if available
            firebase_creds_env = os.getenv('FIREBASE_ADMIN_SDK_JSON')
            if firebase_creds_env:
                logger.info("Found Firebase credentials in environment variable, creating file...")
                try:
                    # Write credentials from environment variable to file
                    with open(cred_path, 'w') as f:
                        f.write(firebase_creds_env)
                    logger.info(f"Successfully created Firebase credentials file from environment variable")
                except Exception as write_error:
                    logger.error(f"Error writing Firebase credentials file: {str(write_error)}")
                    raise
            else:
                raise FileNotFoundError(f"Firebase credentials file not found at {cred_path} and no environment variable available")
        
        # Verify the file has valid content
        try:
            with open(cred_path, 'r') as f:
                creds_content = f.read()
                # Try to parse as JSON to validate
                json.loads(creds_content)
                logger.info(f"Firebase credentials file validated as valid JSON")
        except json.JSONDecodeError:
            logger.error(f"Firebase credentials file is not valid JSON")
            raise ValueError("Firebase credentials file content is not valid JSON")
        except Exception as read_error:
            logger.error(f"Error reading Firebase credentials file: {str(read_error)}")
            raise
            
        # Initialize Firebase with the credentials file
        cred = credentials.Certificate(cred_path)
        project_id = os.getenv('FIREBASE_PROJECT_ID')
        
        if not project_id:
            logger.warning("FIREBASE_PROJECT_ID environment variable not set")
            # Try to extract project_id from credentials file
            try:
                with open(cred_path, 'r') as f:
                    creds_json = json.load(f)
                    project_id = creds_json.get('project_id')
                    logger.info(f"Extracted project_id from credentials file: {project_id}")
            except Exception as e:
                logger.error(f"Failed to extract project_id from credentials: {str(e)}")
        
        logger.info(f"Firebase project ID: {project_id}")
        
        # Check if Firebase is already initialized
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {
                'projectId': project_id
            })
            logger.info("Firebase successfully initialized")
        else:
            logger.info("Firebase already initialized, skipping")
    
    except Exception as e:
        logger.error(f"Error initializing Firebase: {str(e)}")
        logger.error(traceback.format_exc())
        raise


async def verify_firebase_token(request: Request):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    # Debug headers
    logger.debug(f"Request headers: {request.headers}")
    logger.debug(f"Auth header: {request.headers.get('Authorization', 'None')}")
    
    if not token:
        logger.warning("No token provided in Authorization header")
        raise HTTPException(status_code=401, detail='No token provided')

    try:
        logger.debug(f"Verifying token: {token[:10]}...")
        decoded_token = auth.verify_id_token(token)
        
        # Set user_id on request state for later use
        request.state.user_id = decoded_token['uid']
        
        logger.debug(f"Token verified successfully for user: {decoded_token['uid']}")
        return decoded_token
    
    except auth.ExpiredIdTokenError:
        logger.warning("Token expired")
        raise HTTPException(status_code=401, detail='Token expired')
    
    except auth.RevokedIdTokenError:
        logger.warning("Token revoked")
        raise HTTPException(status_code=401, detail='Token revoked')
    
    except auth.InvalidIdTokenError:
        logger.warning("Invalid token")
        raise HTTPException(status_code=401, detail='Invalid token')
    
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=401, detail='Invalid token')
