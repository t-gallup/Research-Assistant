import React, { useState } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "../components/ui/Card";
import { Input } from "../components/ui/Input";
import { Button } from "../components/ui/Button";
import { ChevronDown, ChevronUp, Link as LinkIcon } from "lucide-react";

const QAGenerator = () => {
  const [url, setUrl] = useState("");
  const [expandedQuestion, setExpandedQuestion] = useState(null);

  // Sample questions - in production, these would be generated based on the URL
  const questions = [
    {
      id: 1,
      question:
        "What is a Transformer model and how has it revolutionized data handling?",
      answer:
        "A Transformer is an AI model that revolutionized data handling through its self-attention mechanism, allowing it to process sequences of data in parallel rather than sequentially. It has become the foundation for many modern language models.",
    },
    {
      id: 2,
      question: "What inspired the architecture of Transformers?",
      answer:
        "Transformers were inspired by the encoder-decoder architecture found in RNNs, but innovated by replacing recurrence with self-attention mechanisms. This allowed for better parallel processing and handling of long-range dependencies.",
    },
    {
      id: 3,
      question: "What are the key components of the Transformer encoder layer?",
      answer:
        "The key components include self-attention mechanisms, feed-forward neural networks, and layer normalization. These work together to process input sequences and capture complex relationships in the data.",
    },
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    // Handle URL submission logic here
    console.log("Submitted URL:", url);
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
              />
            </div>
            <Button type="submit">Generate</Button>
          </form>
        </CardContent>
      </Card>

      <div className="space-y-3">
        {questions.map((qa) => (
          <Card
            key={qa.id}
            className="w-full transition-all duration-200 hover:shadow-md"
          >
            <div
              onClick={() =>
                setExpandedQuestion(expandedQuestion === qa.id ? null : qa.id)
              }
              className="flex items-center justify-between p-4 cursor-pointer"
            >
              <h3 className="text-lg font-medium pr-4">{qa.question}</h3>
              {expandedQuestion === qa.id ? (
                <ChevronUp className="h-5 w-5 flex-shrink-0" />
              ) : (
                <ChevronDown className="h-5 w-5 flex-shrink-0" />
              )}
            </div>
            {expandedQuestion === qa.id && (
              <CardContent className="pt-0 pb-4">
                <p className="text-gray-600">{qa.answer}</p>
              </CardContent>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
};

export default QAGenerator;
