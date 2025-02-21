import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from "../components/Card";
import { Button } from "../components/Button";
import Navbar from '../components/Navbar';
import { Loader2 } from "lucide-react";
import { getAuth } from 'firebase/auth';

interface SearchResult {
    title: string;
    link: string;
    snippet: string;
}

const SearchResults = () => {
    const [results, setResults] = useState<SearchResult[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const auth = getAuth()
    
    const navigate = useNavigate();
    
    // Get search query from URL parameters
    const location = useLocation();
    const queryParams = new URLSearchParams(location.search);
    const searchQuery = queryParams.get('q');

    useEffect(() => {
        const fetchResults = async () => {
            if (!searchQuery) {
                setIsLoading(false);
                return;
            }

            try {
                const user = auth.currentUser
                if (!user) {
                    throw new Error('User not authenticated');
                }
                const token = await user.getIdToken();
                const response = await fetch(
                    `${process.env.REACT_APP_API_URL}/api/search?q=${encodeURIComponent(searchQuery)}`,
                    {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    }
                );
                if (!response.ok) {
                    throw new Error('Failed to fetch search results');
                }
                const data = await response.json();
                setResults(data.results);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'An error occurred');
            } finally {
                setIsLoading(false);
            }
        };

        fetchResults();
    }, [searchQuery, auth.currentUser]);

    const handleAnalyzeArticle = async (url: string) => {
        setIsAnalyzing(true);

        const user = auth.currentUser;
        if (!user) {
            console.error("User not authenticated");
            return;
        }
        try {
            const idToken = await user.getIdToken();
            // Store the token or pass it along with the navigation
            // You might want to store this in localStorage or context
            localStorage.setItem('authToken', idToken);
            
            navigate(`/?url=${encodeURIComponent(url)}&autoAnalyze=true`);
        } catch (error) {
            console.error("Error getting auth token:", error);
            setIsAnalyzing(false);
        }
        // Navigate to home page with the URL and autoAnalyze flag
        navigate(`/?url=${encodeURIComponent(url)}&autoAnalyze=true`);
    };

    if (isLoading) {
        return (
            <div className="flex justify-center items-center min-h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-gray-900"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="container mx-auto px-4 py-8">
                <Card className="bg-red-50">
                    <CardHeader>
                        <CardTitle>Error</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-red-600">{error}</p>
                    </CardContent>
                </Card>
            </div>
        );
    }

    return (
        <div className="min-h-screen">
            <Navbar />
            <div className="w-full max-w-4xl mx-auto p-6 space-y-6">
                <h1 className="text-2xl font-bold mb-6 text-white">Search Results for: {searchQuery}</h1>
                
                {results.length === 0 ? (
                    <Card className="bg-gray-800/80 backdrop-blur-sm">
                        <CardContent className="py-4">
                            <p className="text-white">No results found.</p>
                        </CardContent>
                    </Card>
                ) : (
                    <div className="space-y-3">
                        {results.map((result, index) => (
                            <Card
                                key={index}
                                className="hover:shadow-md transition-shadow bg-gray-800/80 backdrop-blur-sm"
                            >
                                <CardContent className="p-6">
                                    <div className="flex flex-col gap-3">
                                        <div className="flex-1">
                                            <h3 className="text-lg font-semibold text-white mb-2 break-words">
                                                {result.title}
                                            </h3>
                                            <p className="text-gray-300 mb-4 break-words">{result.snippet}</p>
                                            <div className="flex gap-3">
                                                <Button
                                                    variant="outline_color"
                                                    size="sm"
                                                    onClick={() => window.open(result.link, "_blank")}
                                                    className="flex items-center gap-2"
                                                >
                                                    View Original
                                                </Button>
                                                <Button
                                                    variant="outline_color"
                                                    size="sm"
                                                    onClick={() => handleAnalyzeArticle(result.link)}
                                                    className="flex items-center gap-2"
                                                    disabled={isAnalyzing}
                                                >
                                                    <Loader2
                                                        className={`h-4 w-4 ${
                                                            isAnalyzing ? "animate-spin" : "hidden"
                                                        }`}
                                                    />
                                                    Analyze Article
                                                </Button>
                                            </div>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default SearchResults;