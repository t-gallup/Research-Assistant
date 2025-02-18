import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/Card";
import Navbar from '../components/Navbar'

interface SearchResult {
    title: string;
    link: string;
    snippet: string;
}

const SearchResults = () => {
    const [results, setResults] = useState<SearchResult[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    
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
                const response = await fetch(`${process.env.REACT_APP_API_URL}/api/search?q=${encodeURIComponent(searchQuery)}`);
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
    }, [searchQuery]);

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
        <div className="container mx-auto px-4 py-8">
            <Navbar />
            <h1 className="text-2xl font-bold mb-6">Search Results for: {searchQuery}</h1>
            
            {results.length === 0 ? (
                <Card>
                    <CardContent className="py-4">
                        <p>No results found.</p>
                    </CardContent>
                </Card>
            ) : (
                <div className="space-y-4">
                    {results.map((result, index) => (
                        <Card key={index} className="hover:shadow-lg transition-shadow">
                            <CardHeader>
                                <CardTitle>
                                    <a href={result.link} 
                                       target="_blank" 
                                       rel="noopener noreferrer"
                                       className="text-blue-600 hover:text-blue-800">
                                        {result.title}
                                    </a>
                                </CardTitle>
                                <CardDescription>
                                    <a href={result.link} 
                                       target="_blank" 
                                       rel="noopener noreferrer"
                                       className="text-green-600">
                                        {result.link}
                                    </a>
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <p className="text-gray-600">{result.snippet}</p>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
};

export default SearchResults;