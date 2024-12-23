const BASE_URL = 'http://localhost:8000';

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
  const response = await fetch(`${BASE_URL}/api/generate-qna`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ url }),
  });

  if (!response.ok) {
    throw new Error('Failed to generate Q&A');
  }

  return response.json();
};