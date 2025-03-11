# Research Assistant: Advanced Content Analysis and Exploration Tool

Research Assistant is a powerful application that transforms how you engage with web content. It automatically analyzes articles and PDFs, generating comprehensive Q&A sets, summaries, audio versions, and recommended related content—making research and learning more efficient and accessible.

## Key Features

### Comprehensive Content Analysis
- **URL-based Analysis**: Paste any web article or PDF link to instantly analyze its content
- **Smart Question & Answer Generation**: AI-powered generation of relevant questions and detailed answers based on the content
- **Concise Article Summaries**: Get the key points of any article in an easy-to-digest format
- **Audio Narration**: Listen to article summaries with high-quality text-to-speech
- **Page-by-Page Summaries**: For PDF documents, get detailed summaries of each page
- **Related Content Discovery**: Find and analyze related articles to explore topics more deeply

### User-Friendly Interface
- **Clean, Modern Design**: Intuitive dark-themed UI with clear navigation
- **Expandable Q&A Format**: Click on questions to reveal detailed answers
- **Multi-Section Layout**: Easily switch between Q&A, Summary, Audio, and Recommendations
- **Interactive Controls**: Listen to audio summaries or analyze related content with a single click
- **Loading Status Indicators**: Clear visual feedback on processing status

### User Management
- **Firebase Authentication**: Secure user accounts with Google sign-in
- **User Profiles**: Personalized experience with user profile management
- **Usage Dashboard**: Track your content analysis usage
- **Subscription Tiers**: Free, Plus, and Pro tiers with different usage limits

### Advanced Technology
- **PDF Processing**: Advanced extraction and analysis of PDF documents
- **HTML Content Processing**: Smart parsing of web article content
- **Audio Generation**: High-quality TTS using Azure Speech Services
- **AI-Powered Analysis**: Using Google's Gemini and OpenAI's GPT models

## Technical Architecture

### Frontend
- **Framework**: React with TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: Firebase Authentication
- **State Management**: React Context API
- **UI Components**: Custom components with Lucide React icons
- **API Integration**: Fetch API for backend communication

### Backend
- **Framework**: FastAPI (Python)
- **Authentication**: Firebase Auth token verification
- **Rate Limiting**: Redis-based rate limiting
- **PDF Processing**: PyMuPDF for PDF extraction
- **Audio Generation**: Azure Speech Services
- **AI Integration**: Google Gemini and OpenAI GPT
- **Related Content**: Google Custom Search API

### Deployment
- **Frontend**: Static hosting
- **Backend**: Containerized deployment
- **Database**: Firestore for user data
- **File Storage**: Server-side storage for audio files

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/t-gallup/Research-Assistant.git
cd Research-Assistant
```

2. Set up the backend:
```bash
cd backend
pip install -r requirements.txt
```

3. Configure environment variables:
Create a `.env` file in the backend directory with:
```
OPENAI_API_KEY=your-openai-api-key
AZURE_SPEECH_KEY=your-azure-speech-key
GOOGLE_API_KEY=your-google-api-key
SEARCH_ENGINE_ID=your-search-engine-id
FIREBASE_SERVICE_ACCOUNT=path-to-your-firebase-service-account-json
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_PRO_PRICE_ID=your-stripe-pro-price-id
STRIPE_PLUS_PRICE_ID=your-stripe-plus-price-id
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret
REDIS_URL=your-redis-url
```

4. Set up the frontend:
```bash
cd frontend
npm install
```

5. Configure frontend environment:
Create a `.env` file in the frontend directory with:
```
REACT_APP_FIREBASE_API_KEY=your-firebase-api-key
REACT_APP_FIREBASE_APP_ID=your-firebase-app-id
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your-firebase-messaging-sender-id
REACT_APP_API_URL=http://localhost:8000
```

6. Start the backend:
```bash
cd backend
uvicorn main:app --reload --port 8000
```

7. Start the frontend (in a new terminal):
```bash
cd frontend
npm start
```

The application will be available at `http://localhost:3000`

## Subscription Plans

### Free Tier
- 10 content analyses per day
- Basic Q&A and summaries
- Audio generation

### Plus Tier
- 30 content analyses per day
- All Free tier features
- Priority processing

### Pro Tier
- 100 content analyses per day
- All Plus tier features
- Advanced analytics
- Faster processing times
