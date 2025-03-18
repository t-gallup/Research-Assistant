/**
 * Application configuration
 * 
 * This file centralizes environment-specific configuration for the Research Assistant app.
 * In production, the API_URL will be set by the AWS Amplify environment variables.
 */

const config = {
  // API URL for backend services - will be overridden by REACT_APP_API_URL env var
  apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  
  // Add other configuration parameters as needed
  // These can be Firebase configuration, feature flags, etc.
};

export default config;
