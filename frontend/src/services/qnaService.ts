import { getAuth } from 'firebase/auth';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

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

  const token = user ? await user.getIdToken() : null;

  if (!token) {
    throw new Error('Not authenticated');
  }
  
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

  if (!response.ok) {
    throw new Error('Failed to generate content');
  }

  return response.json();
};