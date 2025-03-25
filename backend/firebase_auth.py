import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Request
import os
import logging
import traceback
import boto3

# Set up logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def get_secret(secret_name):
    """Retrieve a secret from AWS Secrets Manager"""
    try:
        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )
        
        # Get the secret value
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        
        # Return the secret string
        if 'SecretString' in get_secret_value_response:
            return get_secret_value_response['SecretString']
        else:
            raise ValueError("Secret not found in expected format")
            
    except Exception as e:
        logger.error(f"Error retrieving secret {secret_name}: {str(e)}")
        raise

def init_firebase():
    """Initialize Firebase Admin SDK with credentials from AWS Secrets Manager"""
    try:
        # Check if Firebase is already initialized
        if firebase_admin._apps:
            logger.info("Firebase already initialized")
            return
            
        # Secret name
        secret_name = "firebase-admin-sdk"
        
        try:
            # Get Firebase credentials from Secrets Manager
            logger.info(f"Retrieving Firebase credentials from AWS Secrets Manager: {secret_name}")
            firebase_creds_json = get_secret(secret_name)
            
            # Create temporary file for credentials
            cred_path = "/tmp/firebase-adminsdk.json"
            with open(cred_path, 'w') as f:
                f.write(firebase_creds_json)
            
            # Initialize Firebase with credentials
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            
            # Remove temporary file for security
            os.remove(cred_path)
            
            logger.info("Firebase successfully initialized from Secrets Manager")
            
        except Exception as secrets_error:
            logger.error(f"Failed to initialize from Secrets Manager: {str(secrets_error)}")
            
            # Fallback: Check for environment variable
            firebase_creds_env = os.getenv('FIREBASE_ADMIN_SDK_JSON')
            if firebase_creds_env:
                logger.info("Falling back to environment variable for Firebase credentials")
                
                # Create temporary file for credentials
                cred_path = "/tmp/firebase-adminsdk.json"
                with open(cred_path, 'w') as f:
                    f.write(firebase_creds_env)
                
                # Initialize Firebase with credentials
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                
                # Remove temporary file for security
                os.remove(cred_path)
                
                logger.info("Firebase successfully initialized from environment variable")
                return
            
            # No credentials available, re-raise the original error
            raise secrets_error
            
    except Exception as e:
        logger.error(f"Firebase initialization error: {str(e)}")
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
