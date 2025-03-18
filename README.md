# Research Assistant

An intelligent research assistant app that helps users search, summarize, and interact with scientific papers.

## Features

- Upload and process PDF research papers
- Generate comprehensive summaries
- Ask questions about the papers
- Explore related papers
- Audio summaries with Text-to-Speech
- User authentication and history tracking

## Architecture

### Backend

- FastAPI for API endpoints
- OpenAI integration for LLM capabilities
- Azure Text-to-Speech for audio generation
- Redis for caching and rate limiting
- Firebase for authentication

### Frontend

- React with TypeScript
- Tailwind CSS for styling
- Firebase Authentication

## Deployment Options

### Option 1: Google Cloud (Current)

The app is currently deployed on Google Cloud with:
- Backend on Cloud Run
- Frontend on Cloud Storage with CloudFront
- Redis instance in Google Memorystore
- GitHub Actions for CI/CD workflow

For detailed deployment steps, see the GitHub Actions workflow file.

### Option 2: AWS Amplify

An alternative deployment option is available using AWS services:
- Frontend on AWS Amplify
- Backend options:
  - AWS Lambda with API Gateway (serverless)
  - ECS with Fargate (container-based, better for CUDA workloads)
- Redis on AWS ElastiCache
- Custom domain configuration from GCP

For AWS deployment instructions, see [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md).

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- OpenAI API Key
- Azure Speech Service API Key
- Firebase project

### Local Development

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/research-assistant.git
   cd research-assistant
   ```

2. Set up environment variables
   ```bash
   # Create .env files in both frontend and backend directories
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   
   # Fill in your API keys and configuration
   ```

3. Start the development environment
   ```bash
   docker-compose up -d
   ```

4. Access the application
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## License

[MIT License](LICENSE)
