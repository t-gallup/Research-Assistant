from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import rag_pipeline as rp


class URLInput(BaseModel):
    url: str


app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app's URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.post("/api/generate-qna")
async def generate_qna(url_input: URLInput):
    file_type = rp.check_file_type(url_input.url)
    doc_string, article_title = "", ""
    
    if file_type == "html":
        html = await rp.load_html(url_input.url)
        doc_string, article_title = rp.extract_from_html(html)
    elif file_type == "pdf":
        pdf, response = rp.load_pdf(url_input.url)
        doc_string, article_title = rp.extract_from_pdf(pdf, response)

    final_summary = rp.summarize_content(doc_string)
    topic_list = rp.prompt_llm_for_related_topics(final_summary)
    questions, answers = rp.prompt_llm(final_summary)
    
    # Get recommended articles
    rec_titles, rec_links = [], []
    for topic in topic_list[:2]:
        results = rp.search_google(topic)
        new_rec_titles, new_rec_links = rp.get_top_5_articles(results, url_input.url)
        rec_titles.extend(new_rec_titles)
        rec_links.extend(new_rec_links)

    return {
        "articleTitle": article_title,
        "summary": final_summary,
        "qnaPairs": [{"question": q, "answer": a} for q, a in zip(questions, answers)],
        "recommendedArticles": [{"title": t, "link": l} for t, l in zip(rec_titles, rec_links)]
    }