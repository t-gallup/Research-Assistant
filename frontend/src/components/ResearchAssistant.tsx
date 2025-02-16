// ... Previous imports remain the same ...

const QAGenerator = () => {
  // ... Previous state and handlers remain the same ...

  const sections = [
    // ... Previous sections remain the same until the recommended section ...
    {
      id: "recommended",
      title: "Recommended Articles",
      icon: Newspaper,
      content: (
        <div className="space-y-3">
          {data.recommendedArticles.map((article, index) => (
            <Card key={index} className="hover:shadow-md transition-shadow bg-gray-800/80 backdrop-blur-sm">
              <CardContent className="p-4">
                <div className="flex flex-col gap-4">
                  <h3 className="text-lg font-semibold text-white break-words">
                    {article.title}
                  </h3>
                  <div className="flex flex-wrap gap-3">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => window.open(article.link, '_blank')}
                      className="flex items-center gap-2 text-white border-gray-600 hover:bg-gray-700"
                    >
                      <LinkIcon className="w-4 h-4" />
                      View Original
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setUrl(article.link);
                        setExpandedSection("qna");
                        handleSubmit(new Event("submit") as any);
                      }}
                      className="flex items-center gap-2 text-white border-gray-600 hover:bg-gray-700"
                    >
                      <Loader2
                        className={`h-4 w-4 ${
                          isLoading ? "animate-spin" : "hidden"
                        }`}
                      />
                      Analyze Article
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ),
    },
  ];

  // ... Rest of the component remains the same ...
};

export default QAGenerator;