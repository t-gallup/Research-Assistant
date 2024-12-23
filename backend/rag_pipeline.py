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
import requests
import tensorflow as tf
import ast


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


def summarize_content(doc_string):
    physical_devices = tf.config.list_physical_devices('GPU')
    if physical_devices:
        print("GPU detected, using GPU")
        device = 0
    else:
        print("No GPU detected, using CPU")
        device = -1
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=device)
    max_chunk_size = 1000
    inputs = summarizer.tokenizer(doc_string, return_tensors="tf", truncation=False)
    tokens = inputs.input_ids[0]
    chunks = [tokens[i:i+max_chunk_size] for i in range(0, len(tokens), max_chunk_size)]
    batch_chunk_texts = [summarizer.tokenizer.decode(chunk, skip_special_tokens=True) for chunk in chunks]
    summaries = summarizer(batch_chunk_texts, max_length=100, truncation=True) 
    summary_texts = [summary['summary_text'] for summary in summaries]
    final_summary = " ".join(summary_texts)
    return final_summary


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
    """
    Takes the initial BART summary and refines it using OpenAI to make it more concise and clear.
    """
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
        temperature=0.5,  # Lower temperature for more focused output
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
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": SEARCH_ENGINE_ID,
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
