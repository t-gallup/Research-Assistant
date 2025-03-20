import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Request
import os
import logging
import traceback

# Set up logging
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
            raise FileNotFoundError(f"Firebase credentials file not found at {cred_path}")
        
        cred = credentials.Certificate(cred_path)
        project_id = os.getenv('FIREBASE_PROJECT_ID')
        
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