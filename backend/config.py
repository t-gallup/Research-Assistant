import os
import boto3
from botocore.exceptions import ClientError

# Keep GCP secret manager for backward compatibility
try:
    from google.cloud import secretmanager
    def access_secret_version(project_id, secret_id, version_id="latest"):
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
except ImportError:
    def access_secret_version(project_id, secret_id, version_id="latest"):
        print("Google Cloud Secret Manager not available")
        return None

def get_parameter(name, with_decryption=True):
    """
    Retrieve a parameter from AWS Systems Manager Parameter Store
    """
    ssm = boto3.client('ssm')
    try:
        response = ssm.get_parameter(Name=name, WithDecryption=with_decryption)
        return response['Parameter']['Value']
    except ClientError as e:
        print(f"Error retrieving parameter {name}: {e}")
        return None

def load_secrets():
    # Check for direct environment variables first
    if os.getenv('OPENAI_API_KEY') and os.getenv('AZURE_SPEECH_KEY') and os.getenv('REDIS_PASSWORD'):
        return
        
    # Determine deployment environment
    deployment = os.getenv('DEPLOYMENT', 'unknown').lower()
    
    if deployment == 'aws':
        # AWS Parameter Store path prefix
        prefix = '/research-assistant/'
        
        try:
            secrets = {
                'OPENAI_API_KEY': get_parameter(f"{prefix}openai-api-key"),
                'AZURE_SPEECH_KEY': get_parameter(f"{prefix}azure-speech-key"),
                'REDIS_PASSWORD': get_parameter(f"{prefix}redis-password"),
            }
            
            # Update environment with secrets that were successfully retrieved
            # Filter out None values
            secrets = {k: v for k, v in secrets.items() if v is not None}
            os.environ.update(secrets)
        except Exception as e:
            print(f"Error loading parameters from AWS Parameter Store: {e}")
            
    elif os.getenv('ENVIRONMENT') == 'production':
        # Original GCP Secret Manager implementation
        project_id = os.getenv('GCP_PROJECT_NUMBER')
        try:
            secrets = {
                'OPENAI_API_KEY': access_secret_version(project_id, 'openai-api-key'),
                'AZURE_SPEECH_KEY': access_secret_version(project_id, 'azure-speech-key'),
                'REDIS_PASSWORD': access_secret_version(project_id, 'redis-password'),
            }
            # Update environment with secrets
            secrets = {k: v for k, v in secrets.items() if v is not None}
            os.environ.update(secrets)
        except Exception as e:
            print(f"Error loading secrets from Google Cloud Secret Manager: {e}")
