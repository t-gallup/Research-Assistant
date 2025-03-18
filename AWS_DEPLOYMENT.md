# AWS Deployment Guide for Research Assistant

This guide outlines the steps to deploy the Research Assistant application on AWS infrastructure using AWS Amplify for the frontend and AWS Lambda or ECS for the backend.

## Architecture Overview

The deployment consists of:

1. **Frontend**: React application deployed on AWS Amplify
2. **Backend**: FastAPI application deployed as AWS Lambda or ECS task
3. **Database**: Redis on AWS ElastiCache
4. **Domain**: Custom domain from GCP linked to AWS Amplify

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured locally
- Custom domain registered in GCP (Google Cloud Platform)

## Frontend Deployment with AWS Amplify

1. **Sign in to AWS Console and navigate to AWS Amplify**
2. **Create a new app and connect to your GitHub repository**
   - Choose the "aws-deployment" branch
   - Amplify will automatically detect the React application

3. **Configure build settings**
   - The `amplify.yml` file included in this branch already contains the necessary configuration
   - No additional build settings are required

4. **Set environment variables in the Amplify console**
   - REACT_APP_API_URL: URL of your backend API (added after backend deployment)

5. **Deploy the application**
   - Click "Save and deploy"
   - Amplify will build and deploy your frontend

## Backend Deployment Options

### Option 1: AWS Lambda with API Gateway (Serverless)

1. **Create a Lambda function**
   - Runtime: Python 3.11
   - Handler: lambda.handler
   - Memory: At least 512MB (1024MB recommended)
   - Timeout: 30 seconds (adjust based on your needs)
   - Upload your code as a ZIP file containing the entire backend directory

2. **Set up API Gateway**
   - Create a new REST API
   - Create a proxy resource with `{proxy+}` path
   - Set up ANY method pointing to your Lambda function
   - Deploy the API to a new stage (e.g., "prod")

3. **Set environment variables in Lambda**
   - DEPLOYMENT: aws
   - REDIS_HOST: Your ElastiCache endpoint
   - REDIS_PORT: 6379
   - REDIS_PASSWORD: Your Redis password
   - OPENAI_API_KEY: Your OpenAI API key
   - AZURE_SPEECH_KEY: Your Azure Speech key

### Option 2: Amazon ECS with Fargate (Recommended for CUDA Support)

1. **Create an ECR repository**
   - Navigate to Amazon ECR and create a new repository
   - Push your Docker image to this repository

2. **Create an ECS cluster with Fargate**
   - Navigate to Amazon ECS and create a new cluster
   - Choose the Fargate launch type

3. **Create a task definition**
   - Use the same environment variables as listed for Lambda
   - Allocate appropriate CPU and memory resources
   - Use the ECR image you pushed earlier

4. **Create a service**
   - Use the task definition you created
   - Configure desired number of tasks (e.g., 1 for development, more for production)
   - Set up Application Load Balancer for routing traffic

## Redis Setup with AWS ElastiCache

1. **Create an ElastiCache Redis cluster**
   - Navigate to ElastiCache in the AWS Console
   - Create a new Redis cluster
   - Choose an appropriate node type
   - Enable encryption and set a password

2. **Configure security groups**
   - Allow inbound traffic from your Lambda or ECS tasks
   - Restrict access to only necessary services

## Domain Configuration

1. **In AWS Amplify, navigate to "Domain Management"**
   - Add your GCP custom domain
   - Amplify will provide DNS records to add to your GCP DNS configuration

2. **In Google Cloud Console, update DNS settings**
   - Navigate to Cloud DNS
   - Add the CNAME records provided by AWS Amplify
   - Wait for DNS propagation (can take up to 48 hours)

## Monitoring and Logging

1. **Set up CloudWatch Logs**
   - Both Lambda and ECS automatically integrate with CloudWatch Logs
   - Create log groups and metrics as needed

2. **Configure alarms**
   - Set up CloudWatch Alarms for critical metrics
   - Configure notifications for alarm triggers

## Maintenance and Updates

To update your application:

1. **Push changes to the GitHub repository**
2. **Amplify will automatically rebuild and deploy the frontend**
3. **For backend updates:**
   - If using Lambda: Upload new code package
   - If using ECS: Push new Docker image and update the task definition

## Troubleshooting

- **Check CloudWatch Logs** for application errors
- **Verify environment variables** are correctly set
- **Ensure security groups** allow proper communication between services
- **Check Redis connection** status from your backend

## Cost Optimization

- Use Amplify's free tier for frontend hosting
- Consider Lambda for backend if usage is sporadic
- Use ECS with Fargate if more consistent or GPU-intensive workloads are needed
- Enable auto-scaling to optimize costs during varying loads
