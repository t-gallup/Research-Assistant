from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
from langchain_community.document_loaders import PyPDFLoader
from transformers import pipeline
from tempfile import NamedTemporaryFile
from PyPDF2 import PdfReader
from io import BytesIO
import openai
import re
import os
import ast
import requests
import logging
from google.cloud import aiplatform
from google.cloud import storage
from dotenv import load_dotenv
import json

load_dotenv()

logger = logging.getLogger(__name__)


class GCPSummarizer:
    def __init__(self):
        self.project_id = os.getenv('GCP_PROJECT_ID')
        self.region = os.getenv('GCP_REGION', 'us-west1')
        self.bucket_name = "summarizationbucket"

        aiplatform.init(
            project=self.project_id,
            location=self.region,
            staging_bucket=self.bucket_name
        )

        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(self.bucket_name)

    def submit_job(self, text: str) -> str:
        try:
            container_spec = {
                "image_uri": f"gcr.io/{self.project_id}/pytorch-gpu",
                "command": ["python", "summarize_script.py"],
                "args": [f"--text={text}"]
            }

            worker_pool_specs = [{
                "machine_spec": {
                    "machine_type": "n1-standard-8",
                    "accelerator_type": "NVIDIA_TESLA_T4",
                    "accelerator_count": 1
                },
                "replica_count": 1,
                "container_spec": container_spec
            }]

            job = aiplatform.CustomJob(
                display_name="summarization-job",
                worker_pool_specs=worker_pool_specs
            )

            job.run(sync=True)
            
            blob = self.bucket.blob('summary.json')
            content = blob.download_as_string()
            result = json.loads(content)
            
            return result["summary"]
            
        except Exception as e:
            logger.error(f"Error in GCP job submission: {str(e)}")
            raise


def check_file_type(url):
    response = requests.head(url, allow_redirects=True)
    content_type = response.headers.get('Content-Type', '').lower()
    
    if 'application/pdf' in content_type:
        return 'pdf'
    elif 'text/html' in content_type:
        return 'html'
    else:
        return 'unknown'


async def load_html(url):
    loader = AsyncHtmlLoader(url)
    html = loader.load()
    return html


def extract_from_html(html):
    bs_transformer = BeautifulSoupTransformer()
    tags_to_extract = ["p", "span", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li"]
    docs_transformed = bs_transformer.transform_documents(html, tags_to_extract=tags_to_extract)
    doc_string = ""
    for doc in docs_transformed:
        doc_string += doc.page_content
    titles_transformed = bs_transformer.transform_documents(html, tags_to_extract=["title"])
    article_title = titles_transformed[0].metadata['title']
    return doc_string, article_title


def load_pdf(url):
    response = requests.get(url)
    with NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
        temp_pdf.write(response.content)
        temp_pdf_path = temp_pdf.name
    loader = PyPDFLoader(temp_pdf_path)
    pdf = loader.load()
    os.remove(temp_pdf_path)
    return pdf, response


def extract_from_pdf(pdf, response):
    doc_string = ""
    for doc in pdf:
        doc_string += doc.page_content

    pdf_content = BytesIO(response.content)
    reader = PdfReader(pdf_content)
    metadata = reader.metadata
    article_title = metadata.title if metadata.title else ""
    return doc_string, article_title


def summarize_content(text: str) -> str:
    """Summarize content using Google Cloud GPU"""
    try:
        # Initialize GCP summarizer
        summarizer = GCPSummarizer()
        
        # Submit job and get summary
        summary = summarizer.submit_job(text)
        return summary

    except Exception as e:
        logger.error(f"Error in GCP summarization: {str(e)}")
        # Fallback to local CPU if GCP fails
        logger.info("Falling back to local CPU summarization")
        summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            device=-1
        )
        summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
        return summary[0]['summary_text']


def prompt_llm(final_summary):
    prompt = f"""
    Based on the following content: {final_summary} generate 10-15 questions 
    that will help readers understand the content better then provide
    informative answers to these questions.
    Only give questions that can be answered from the content of the article.
    Ensure each question is immediately followed by its answer without adding any labels like "Question" or "Answer". 
    Just output the question followed directly by the answer.
    Make sure you don't use LaTeX in your questions and answers.
    """
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant who generates FAQs from website content."},
            {"role": "user", "content": prompt},
        ]
    )
    answer = response.choices[0].message.content
    faq_list = re.split(r"\n+", answer)
    questions = [faq for i, faq in enumerate(faq_list) if i % 2 == 0]
    answers = [faq for i, faq in enumerate(faq_list) if i % 2 == 1]
    return questions, answers


def refine_summary(initial_summary):
    prompt = f"""
    You are an expert at making technical content clear and accessible. Rewrite the following
    technical summary to be more concise and easier to understand. Focus on:
    
    1. Key concepts and main ideas
    2. Clear, simple language without jargon
    3. Logical flow of ideas
    4. Brevity while maintaining important details
    
    Summary to refine: {initial_summary}
    
    Format your response as a polished, well-organized paragraph that a general audience can understand.
    Aim for around 2-3 sentences that capture the essence of the content.
    """

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert at making complex technical content clear and concise."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
    )
    
    refined_summary = response.choices[0].message.content.strip()
    return refined_summary


def prompt_llm_for_related_topics(final_summary):
    prompt = f"""
    Based on the following content: {final_summary} generate exactly 2 topics
    that are related to this topic or discussed in the article summary.
    Provide your answer in the format '['Topic 1', 'Topic 2']'
    """

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant who generates topics related to article summaries."},
            {"role": "user", "content": prompt},
        ]
    )
    topic_list_str = response.choices[0].message.content
    topic_list = ast.literal_eval(topic_list_str)
    return topic_list


def search_google(query):
    google_api_key = os.getenv("GOOGLE_API_KEY")
    search_engine_id = os.getenv("SEARCH_ENGINE_ID")
    
    if not google_api_key or not search_engine_id:
        raise ValueError("Missing required Google API credentials")
        
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": google_api_key,
        "cx": search_engine_id,
        "q": query,
    }
    response = requests.get(url, params=params)
    results = response.json()
    return results


def get_top_5_articles(results, past_url):
    titles = []
    links = []
    for i in range(5):
        if 'items' in results and results['items'][i]['link'] != past_url:
            titles.append(results['items'][i]['title'])
            links.append(results['items'][i]['link'])
    return titles, links
