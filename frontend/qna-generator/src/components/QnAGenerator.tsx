import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Loader2 } from 'lucide-react';
import { generateQnA } from '../services/qnaService.ts';
import { Alert, AlertDescription } from './ui/Alert.tsx';

interface QnAPair {
  question: string;
  answer: string;
}

interface RecommendedArticle {
  title: string;
  link: string;
}

const QnAGenerator = () => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusText, setStatusText] = useState('');
  const [articleTitle, setArticleTitle] = useState('');
  const [summary, setSummary] = useState('');
  const [qnaPairs, setQnaPairs] = useState<QnAPair[]>([]);
  const [recommendedArticles, setRecommendedArticles] = useState<RecommendedArticle[]>([]);
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  const generateFAQ = async (inputUrl: string) => {
    setLoading(true);
    setProgress(0);
    setStatusText('Loading website content...');

    try {
      const response = await generateQnA(inputUrl);
      
      setArticleTitle(response.articleTitle);
      setSummary(response.summary);
      setQnaPairs(response.qnaPairs);
      setRecommendedArticles(response.recommendedArticles);

      setProgress(100);
      setStatusText('Q&A generation complete...');
    } catch (error) {
      setStatusText('Error generating Q&A');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url) generateFAQ(url);
  };

  return (
    <div className="flex min-h-screen bg-gray-50">
      <main className="flex-1 p-8 max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Q&A Generator</h1>
        
        <form onSubmit={handleSubmit} className="mb-8">
          <div className="flex gap-4">
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Enter website URL to learn about..."
              className="flex-1 p-3 border rounded-lg text-lg"
            />
            <button
              type="submit"
              disabled={loading || !url}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg disabled:bg-blue-300"
            >
              Generate
            </button>
          </div>
        </form>

        {loading && (
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-2">
              <Loader2 className="animate-spin" />
              <span>{statusText}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-blue-600 h-2.5 rounded-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        {articleTitle && (
          <h2 className="text-2xl font-semibold mb-4">{articleTitle}</h2>
        )}

        {qnaPairs.map((pair, index) => (
          <div key={index} className="mb-4">
            <button
              onClick={() => setExpandedIndex(expandedIndex === index ? null : index)}
              className="w-full flex justify-between items-center p-4 bg-white rounded-lg shadow hover:bg-gray-50"
            >
              <span className="font-medium">{pair.question}</span>
              {expandedIndex === index ? <ChevronUp /> : <ChevronDown />}
            </button>
            {expandedIndex === index && (
              <div className="p-4 bg-gray-50 rounded-b-lg mt-1">
                {pair.answer}
              </div>
            )}
          </div>
        ))}

        {summary && (
          <Alert className="mt-8">
            <AlertDescription>
              <strong>Article Summary:</strong> {summary}
            </AlertDescription>
          </Alert>
        )}
      </main>

      <aside className="w-72 p-6 bg-white border-l">
        <h2 className="text-xl font-semibold mb-4">Recommended Articles</h2>
        <div className="space-y-2">
          {recommendedArticles.map((article, index) => (
            <button
              key={index}
              onClick={() => {
                setUrl(article.link);
                generateFAQ(article.link);
              }}
              className="w-full text-left p-3 text-sm hover:bg-gray-50 rounded-lg"
            >
              {article.title}
            </button>
          ))}
        </div>
      </aside>
    </div>
  );
};

export default QnAGenerator;