import { getAuth } from 'firebase/auth';

// Use environment variable for API URL with fallback
const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
console.log("QNA Service using API URL:", BASE_URL); // Debug logging

export interface QnAResponse {
  articleTitle: string;
  summary: string;
  qnaPairs: Array<{
    question: string;
    answer: string;
  }>;
  recommendedArticles: Array<{
    title: string;
    link: string;
  }>;
}

export const generateQnA = async (url: string): Promise<QnAResponse> => {
  const auth = getAuth();
  const user = auth.currentUser;

  if (!user) {
    throw new Error('Not authenticated');
  }
  
  const token = await user.getIdToken();
  console.log(`Making API request to ${BASE_URL}/api/generate-qna`); // Debug logging
  
  const response = await fetch(`${BASE_URL}/api/generate-qna`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    credentials: 'include',
    body: JSON.stringify({ url }),
  });

  console.log(`API response status: ${response.status}`); // Debug logging
  
  if (!response.ok) {
    console.error(`API error: ${response.status} ${response.statusText}`);
    const errorText = await response.text();
    console.error(`Error details: ${errorText}`);
    throw new Error('Failed to generate content');
  }

  const data = await response.json();
  console.log('Successfully received API response'); // Debug logging
  return data;
};