import React, { useState, useEffect, useCallback } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "../components/Card";
import { Input } from "../components/Input";
import { Button } from "../components/Button";
import Navbar from "../components/Navbar";
import { useLocation } from "react-router-dom";
import {
  ChevronDown,
  ChevronUp,
  Link as LinkIcon,
  Play,
  BookOpen,
  List,
  Newspaper,
  Loader2,
  FileText,
  CheckCircle2
} from "lucide-react";
import { Alert, AlertTitle, AlertDescription } from "../components/Alert";
import { getAuth } from 'firebase/auth';

const BASE_URL = "http://localhost:8000";

const ResearchAssistant = () => {
  const [url, setUrl] = useState("");
  const [expandedQuestions, setExpandedQuestions] = useState(new Set());
  const [expandedChunkSummaries, setExpandedChunkSummaries] = useState(new Set());
  const [expandedSection, setExpandedSection] = useState("qna");
  const [data, setData] = useState({
    articleTitle: "",
    summary: "",
    qnaPairs: [],
    recommendedArticles: [],
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [audioFile, setAudioFile] = useState<string | null>(null);
  const [chunkSummaries, setChunkSummaries] = useState([]);
  const [loadingStage, setLoadingStage] = useState<{
    current: 'idle' | 'qna' | 'audio' | 'complete';
    completed: string[];
  }>({ current: 'idle', completed: [] });

  // Get URL and autoAnalyze parameters
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const urlParam = queryParams.get('url');
  const autoAnalyze = queryParams.get('autoAnalyze');

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    setLoadingStage({ current: 'qna', completed: [] });

    try {
      const auth = getAuth()
      const user = auth.currentUser

      if (!user) {
        setError("Please sign in to continue");
        setIsLoading(false);
        setLoadingStage({ current: 'idle', completed: [] });
        return;
      }

      const token = await user.getIdToken();

      // QNA Generation
      const qnaResponse = await fetch(`${BASE_URL}/api/generate-qna`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ url }),
      });

      if (!qnaResponse.ok) {
        if (qnaResponse.status === 401) {
            setError("Authentication failed. Please sign in again.");
        } else if (qnaResponse.status === 429) {
            setError("Rate limit exceeded. Please try again later.");
        } else {
            setError("Failed to generate content");
        }
        setLoadingStage({ current: 'idle', completed: [] });
        return;
      }

      const responseData = await qnaResponse.json();
      setData(responseData);
      setLoadingStage(prev => ({ 
        current: 'audio', 
        completed: [...prev.completed, 'Content Analysis & Q&A Generation'] 
      }));

      // Audio Generation
      const audioResponse = await fetch(`${BASE_URL}/api/generate-audio`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ url }),
      });

      if (!audioResponse.ok) {
        if (audioResponse.status === 401) {
            setError("Authentication failed. Please sign in again.");
        } else if (audioResponse.status === 429) {
            setError("Rate limit exceeded. Please try again later.");
        } else {
            setError("Failed to generate content");
        }
        return;
      }

      const audioData = await audioResponse.json();
      if (audioData.audio_file) {
        setAudioFile(audioData.audio_file);
      }
      if (audioData.chunk_summaries) {
        setChunkSummaries(audioData.chunk_summaries);
      }
      setLoadingStage(prev => ({
        current: 'complete',
        completed: [...prev.completed, 'Audio Generation & Page Summaries']
      }));
    } catch (err) {
      setError(err.message);
      console.error("Error:", err);
    } finally {
      setIsLoading(false);
    }
  }, [url]);
  
  useEffect(() => {
    if (urlParam && autoAnalyze === 'true') {
        setUrl(urlParam);
        
        const autoSubmit = async () => {
            setError(null);
            setIsLoading(true);
            setLoadingStage({ current: 'qna', completed: [] });

            try {
                const auth = getAuth();
                const user = auth.currentUser;

                if (!user) {
                    setError("Please sign in to continue");
                    setIsLoading(false);
                    setLoadingStage({ current: 'idle', completed: [] });
                    return;
                }

                const token = await user.getIdToken();

                // QNA Generation
                const qnaResponse = await fetch(`${BASE_URL}/api/generate-qna`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`
                    },
                    body: JSON.stringify({ url: urlParam }),
                });

                if (!qnaResponse.ok) {
                    if (qnaResponse.status === 401) {
                        setError("Authentication failed. Please sign in again.");
                    } else if (qnaResponse.status === 429) {
                        setError("Rate limit exceeded. Please try again later.");
                    } else {
                        setError("Failed to generate content");
                    }
                    setIsLoading(false);
                    setLoadingStage({ current: 'idle', completed: [] });
                    return;
                }

                const responseData = await qnaResponse.json();
                setData(responseData);
                setLoadingStage(prev => ({ 
                  current: 'audio', 
                  completed: [...prev.completed, 'Content Analysis & Q&A Generation'] 
                }));

                // Audio Generation
                const audioResponse = await fetch(`${BASE_URL}/api/generate-audio`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`
                    },
                    body: JSON.stringify({ url: urlParam }),
                });

                if (!audioResponse.ok) {
                    if (audioResponse.status === 401) {
                        setError("Authentication failed. Please sign in again.");
                    } else if (audioResponse.status === 429) {
                        setError("Rate limit exceeded. Please try again later.");
                    } else {
                        setError("Failed to generate audio content");
                    }
                    setIsLoading(false);
                    return;
                }

                const audioData = await audioResponse.json();
                if (audioData.audio_file) {
                    setAudioFile(audioData.audio_file);
                }
                if (audioData.chunk_summaries) {
                    setChunkSummaries(audioData.chunk_summaries);
                }
                setLoadingStage(prev => ({
                  current: 'complete',
                  completed: [...prev.completed, 'Audio Generation & Page Summaries']
                }));

            } catch (err) {
                setError(err.message);
                console.error("Error:", err);
            } finally {
                setIsLoading(false);
            }
        };

        autoSubmit();
    }
}, [urlParam, autoAnalyze]);

  const sections = [/* ... existing sections code ... */];

  const LoadingStageIndicator = () => {
    if (!isLoading && loadingStage.current === 'idle') return null;

    const stages = [
      { id: 'qna', label: 'Content Analysis & Q&A Generation' },
      { id: 'audio', label: 'Audio Generation & Page Summaries' },
    ];

    return (
      <Card className="w-full bg-gray-800/80 backdrop-blur-sm">
        <CardContent className="p-4">
          <div className="space-y-3">
            {stages.map((stage) => (
              <div key={stage.id} className="flex items-center gap-3">
                {loadingStage.completed.includes(stage.label) ? (
                  <CheckCircle2 className="h-5 w-5 text-green-500" />
                ) : loadingStage.current === stage.id ? (
                  <Loader2 className="h-5 w-5 animate-spin text-blue-500" />
                ) : (
                  <div className="h-5 w-5 rounded-full border-2 border-gray-600" />
                )}
                <span className={`text-sm ${
                  loadingStage.completed.includes(stage.label) 
                    ? 'text-green-500' 
                    : loadingStage.current === stage.id
                    ? 'text-blue-500'
                    : 'text-gray-400'
                }`}>
                  {stage.label}
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="min-h-screen">
      <Navbar />
      <div className="w-full max-w-4xl mx-auto p-6 space-y-6">
        <Card className="w-full bg-gray-800/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-2xl font-bold text-white">
              Explore Content
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="flex gap-2">
              <div className="relative flex-1">
                <LinkIcon className="absolute left-2 top-2.5 h-5 w-5 text-gray-400" />
                <Input
                  type="url"
                  placeholder="Enter URL..."
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="pl-9 bg-gray-700/60 text-white border-gray-600 placeholder-gray-400"
                  disabled={isLoading}
                />
              </div>
              <Button
                variant="outline_color"
                type="submit"
                disabled={isLoading || !url}
                className=""
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  "Analyze"
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {isLoading && <LoadingStageIndicator />}

        {error && (
          <Alert variant="destructive">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Rest of the existing JSX */}
      </div>
    </div>
  );
};

export default ResearchAssistant;