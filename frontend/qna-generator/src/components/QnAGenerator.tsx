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
} from "lucide-react";
import { Alert, AlertTitle, AlertDescription } from "../components/ui/Alert";

const BASE_URL = 'http://localhost:8000';

const QAGenerator = () => {
  const [url, setUrl] = useState("");
  const [expandedQuestion, setExpandedQuestion] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      // Update the API endpoint to use localhost on port 8000
      const response = await fetch(`${BASE_URL}/api/generate-qa`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate questions");
      }

      const data = await response.json();
      setQuestions(data.questions);
    } catch (err) {
      setError(err.message);
      setQuestions([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto p-4 space-y-6">
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">Q&A Generator</CardTitle>
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
                  Generating...
                </>
              ) : (
                "Generate"
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

      {questions.length > 0 && (
        <div className="space-y-3">
          {questions.map((qa, index) => (
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
      )}
    </div>
  );
};

export default QAGenerator;
