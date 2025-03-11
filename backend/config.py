from google.cloud import secretmanager
import os


def access_secret_version(project_id, secret_id, version_id="latest"):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


def load_secrets():
    if os.getenv('ENVIRONMENT') == 'production':
        project_id = os.getenv('GCP_PROJECT_NUMBER')
        secrets = {
            'OPENAI_API_KEY': access_secret_version(project_id, 'openai-api-key'),
            'AZURE_SPEECH_KEY': access_secret_version(project_id, 'azure-speech-key'),
            'REDIS_PASSWORD': access_secret_version(project_id, 'redis-password'),
        }
        # Update environment with secrets
        os.environ.update(secrets)
