from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import rag_pipeline as rp
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class URLInput(BaseModel):
    url: str


app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/generate-qna")
async def generate_qna(url_input: URLInput):
    try:
        logger.info(f"Processing URL: {url_input.url}")
        
        file_type = rp.check_file_type(url_input.url)
        doc_string, article_title = "", ""
        
        if file_type == "html":
            html = await rp.load_html(url_input.url)
            doc_string, article_title = rp.extract_from_html(html)
        elif file_type == "pdf":
            pdf, response = rp.load_pdf(url_input.url)
            doc_string, article_title = rp.extract_from_pdf(pdf, response)

        logger.info("Initial content extracted")

        # Get initial summary using BART
        initial_summary = rp.summarize_content(doc_string)
        logger.info("Initial summary generated")

        # Refine the summary using OpenAI
        refined_summary = rp.refine_summary(initial_summary)
        logger.info("Summary refined")

        topic_list = rp.prompt_llm_for_related_topics(refined_summary)
        questions, answers = rp.prompt_llm(refined_summary)
        logger.info("Q&A generated")

        # Get recommended articles
        rec_titles, rec_links = [], []
        for topic in topic_list[:2]:
            results = rp.search_google(topic)
            new_rec_titles, new_rec_links = rp.get_top_5_articles(results, url_input.url)
            rec_titles.extend(new_rec_titles)
            rec_links.extend(new_rec_links)

        logger.info("Recommended articles retrieved")

        return {
            "articleTitle": article_title,
            "summary": refined_summary,
            "qnaPairs": [{"question": q, "answer": a} for q, a in zip(questions, answers)],
            "recommendedArticles": [{"title": t, "link": l} for t, l in zip(rec_titles, rec_links)]
        }
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
