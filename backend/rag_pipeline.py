from PyPDF2 import PdfReader
from io import BytesIO
import openai
import re
import os
import ast
import requests
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types
import httpx
from bs4 import BeautifulSoup
import fitz

load_dotenv()

logger = logging.getLogger(__name__)


def extract_arxiv_title(pdf_url):
    """Extract title from arXiv papers"""
    
    # Download the PDF
    response = requests.get(pdf_url)
    pdf_data = BytesIO(response.content)
    
    # Try to extract arXiv ID first
    arxiv_id = None
    if "arxiv.org" in pdf_url:
        arxiv_id_match = re.search(r'(\d+\.\d+)', pdf_url)
        if arxiv_id_match:
            arxiv_id = arxiv_id_match.group(1)
    
    # If we have arxiv_id, try the API method first
    if arxiv_id:
        try:
            api_url = f"https://export.arxiv.org/api/query?id_list={arxiv_id}"
            response = requests.get(api_url)
            if response.status_code == 200:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)
                # Extract title from XML (using proper XML namespaces)
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                title_elem = root.find('.//atom:entry/atom:title', ns)
                if title_elem is not None and title_elem.text:
                    return title_elem.text.strip()
        except Exception as e:
            print(f"API method failed: {e}")
    
    # Fallback to direct PDF extraction
    try:
        doc = fitz.open(stream=pdf_data, filetype="pdf")
        
        # Strategy 1: Look for largest text on first page
        page = doc[0]
        blocks = page.get_text("dict")["blocks"]
        largest_size = 0
        largest_text = ""
        
        # Find text with largest font size
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        if span["size"] > largest_size and len(span["text"].strip()) > 10:
                            largest_size = span["size"]
                            largest_text = span["text"].strip()
        
        if largest_text:
            return largest_text
            
        # Strategy 2: Get first few lines and look for a title-like pattern
        text = page.get_text("text").strip().split('\n')
        for i in range(min(5, len(text))):
            line = text[i].strip()
            # Title likely characteristics: not too short, not too long, no trailing period
            if 15 <= len(line) <= 100 and not line.endswith('.') and not line.startswith('http'):
                return line
                
        # Strategy 3: Try getting text from the top of the page
        blocks.sort(key=lambda b: b["bbox"][1])
        if blocks and "lines" in blocks[0] and blocks[0]["lines"]:
            first_line = blocks[0]["lines"][0]
            if "spans" in first_line and first_line["spans"]:
                return first_line["spans"][0]["text"].strip()
                
        # Fallback to traditional metadata
        if doc.metadata and doc.metadata.get("title"):
            return doc.metadata.get("title")
            
        return "Untitled Document"
            
    except Exception as e:
        print(f"PDF extraction failed: {e}")
        return "Extraction Failed"
    finally:
        if 'doc' in locals():
            doc.close()


def summarize_content(url):
    client = genai.Client()
    doc_data = httpx.get(url)
    content_type = doc_data.headers.get('Content-Type', '')

    prompt = "Summarize this document"
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=[
            types.Part.from_bytes(
                data=doc_data.content,
                mime_type=content_type,
            ),
            prompt])
    title = ""
    if content_type == 'application/pdf':
        pdf_file = BytesIO(doc_data.content)
        try:
            pdf_reader = PdfReader(pdf_file)
            # Try to get title from PDF metadata
            title = pdf_reader.metadata.get('/Title', '')
            if title == '':
                title = extract_arxiv_title(url)
        except Exception as e:
            logger.exception(e)
            pass
    if content_type == 'text/html':
        soup = BeautifulSoup(doc_data.text, 'html.parser')
        title = ""
        if soup.title:
            title = soup.title.string.strip()
        if not title:
            meta_title = soup.find('meta', property='og:title')
            if meta_title:
                title = meta_title.get('content', '').strip()
        if not title:
            meta_title = soup.find('meta', attrs={'name': 'title'})
            if meta_title:
                title = meta_title.get('content', '').strip()
    
    return response.text, title


def prompt_llm(final_summary):
    prompt = f"""
    Based on the following content: {final_summary} generate 10-15 questions
    that will help readers understand the content better then provide
    informative answers to these questions.
    Only give questions that can be answered from the content of the article.
    For the answers, don't say this question was answered in the document,
    instead just provide the answer from the document.
    Ensure each question is immediately followed by its answer without adding any labels like "Question" or "Answer". 
    Just output the question followed directly by the answer.
    Make sure you don't use LaTeX in your questions and answers.
    """
    openai.api_key = os.getenv('OPENAI_API_KEY')
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



def prompt_llm_for_related_topics(final_summary):
    prompt = f"""
    Based on the following content: {final_summary} generate exactly 2 topics
    that are related to this topic or discussed in the article summary.
    Provide your answer in the format '['Topic 1', 'Topic 2']'
    """
    openai.api_key = os.getenv('OPENAI_API_KEY')
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
    for item in results['items'][:5]:
        if 'items' in results and item['link'] != past_url:
            titles.append(item['title'])
            links.append(item['link'])
    return titles, links
