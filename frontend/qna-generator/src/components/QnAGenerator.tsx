import React, { useState } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "../components/ui/Card";
import { Input } from "../components/ui/Input";
import { Button } from "../components/ui/Button";
import {
  ChevronDown,
  ChevronUp,
  Link as LinkIcon,
  Loader2,
  BookOpen,
  List,
  Newspaper
} from "lucide-react";
import { Alert, AlertTitle, AlertDescription } from "../components/ui/Alert";

const BASE_URL = 'http://localhost:8000';

const QAGenerator = () => {
  const [url, setUrl] = useState("");
  const [expandedQuestion, setExpandedQuestion] = useState(null);
  const [expandedSection, setExpandedSection] = useState("qna"); // Default to Q&A section
  const [data, setData] = useState({
    articleTitle: "",
    summary: "",
    qnaPairs: [],
    recommendedArticles: []
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const response = await fetch(`${BASE_URL}/api/generate-qna`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate content");
      }

      const responseData = await response.json();
      setData(responseData);
    } catch (err) {
      setError(err.message);
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
              className="w-full transition-all duration-200 hover:shadow-md"
            >
              <div
                onClick={() =>
                  setExpandedQuestion(expandedQuestion === index ? null : index)
                }
                className="flex items-center justify-between p-4 cursor-pointer"
              >
                <h3 className="text-lg font-medium pr-4">{qa.question}</h3>
                {expandedQuestion === index ? (
                  <ChevronUp className="h-5 w-5 flex-shrink-0" />
                ) : (
                  <ChevronDown className="h-5 w-5 flex-shrink-0" />
                )}
              </div>
              {expandedQuestion === index && (
                <CardContent className="pt-0 pb-4">
                  <p className="text-gray-600">{qa.answer}</p>
                </CardContent>
              )}
            </Card>
          ))}
        </div>
      ),
    },
    {
      id: "summary",
      title: "Article Summary",
      icon: BookOpen,
      content: (
        <Card>
          <CardContent className="pt-6">
            <h2 className="text-xl font-bold mb-4">{data.articleTitle}</h2>
            <p className="text-gray-600 whitespace-pre-wrap">{data.summary}</p>
          </CardContent>
        </Card>
      ),
    },
    {
      id: "recommended",
      title: "Recommended Articles",
      icon: Newspaper,
      content: (
        <div className="space-y-3">
          {data.recommendedArticles.map((article, index) => (
            <Card key={index}>
              <CardContent className="p-4">
                <a
                  href={article.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 font-medium"
                >
                  {article.title}
                </a>
              </CardContent>
            </Card>
          ))}
        </div>
      ),
    },
  ];

  return (
    <div className="w-full max-w-4xl mx-auto p-4 space-y-6">
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">Content Explorer</CardTitle>
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
                className="pl-9"
                disabled={isLoading}
              />
            </div>
            <Button type="submit" disabled={isLoading || !url}>
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

      {error && (
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {(data.qnaPairs.length > 0 || data.summary || data.recommendedArticles.length > 0) && (
        <div className="space-y-4">
          <div className="flex gap-2 border-b pb-2">
            {sections.map((section) => (
              <Button
                key={section.id}
                variant={expandedSection === section.id ? "default" : "outline"}
                onClick={() => setExpandedSection(section.id)}
                className="flex items-center gap-2"
              >
                <section.icon className="h-4 w-4" />
                {section.title}
              </Button>
            ))}
          </div>
          <div className="min-h-[200px]">
            {sections.find((s) => s.id === expandedSection)?.content}
          </div>
        </div>
      )}
    </div>
  );
};

export default QAGenerator;