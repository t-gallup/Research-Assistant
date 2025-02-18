import React, { useState, useEffect } from "react";
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
  FileText
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

  // Get URL and autoAnalyze parameters
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const urlParam = queryParams.get('url');
  const autoAnalyze = queryParams.get('autoAnalyze');

  useEffect(() => {
    // If URL and autoAnalyze are present in parameters, trigger analysis
    if (urlParam && autoAnalyze === 'true') {
      setUrl(urlParam);
      handleSubmit(new Event('submit') as any);
    }
  }, [urlParam, autoAnalyze]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const auth = getAuth()
      const user = auth.currentUser

      if (!user) {
        setError("Please sign in to continue");
        setIsLoading(false);
        return;
      }

      const token = await user.getIdToken();

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
            throw new Error("Failed to generate content");
        }
        return;
      }

      const responseData = await qnaResponse.json();
      setData(responseData);

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
            throw new Error("Failed to generate content");
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
    } catch (err) {
      setError(err.message);
      console.error("Error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const sections = [
    {
      id: "qna",
      title: "Questions & Answers",
      icon: List,
      content: (
        <div className="space-y-3">
          {data.qnaPairs.map((qa, index) => (
            <Card
              key={index}
              className="w-full transition-all duration-200 hover:shadow-md bg-gray-800/80 backdrop-blur-sm"
            >
              <div
                onClick={() => {
                  setExpandedQuestions(prev => {
                    const newSet = new Set(prev);
                    if (newSet.has(index)) {
                      newSet.delete(index);
                    } else {
                      newSet.add(index);
                    }
                    return newSet;
                  });
                }} className="flex justify-between items-center"
              >
                <h3 className="text-lg font-semibold p-4 text-white">
                  {qa.question}
                </h3>
                {expandedQuestions.has(index) ? (
                  <ChevronUp className="h-5 flex-shrink-0 pr-2 text-white" />
                ) : (
                  <ChevronDown className="h-5 flex-shrink-0 pr-2 text-white" />
                )}
              </div>
              {expandedQuestions.has(index) && (
                <CardContent className="pt-0 pb-4 px-4">
                  <p className="text-gray-300 leading-relaxed text-base">
                    {qa.answer}
                  </p>
                </CardContent>
              )}
            </Card>
          ))}
        </div>
      ),
    },