from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
from transformers import pipeline
import openai
import re
import os
import requests
import tensorflow as tf
import ast

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

def summarize_content(doc_string):
    physical_devices = tf.config.list_physical_devices('GPU')
    if physical_devices:
        print("GPU detected, using GPU for summarization")
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
    summaries = summarizer(batch_chunk_texts, max_length=1000, truncation=True) 
    summary_texts = [summary['summary_text'] for summary in summaries]
    final_summary = " ".join(summary_texts)
    return final_summary

def prompt_llm(final_summary):
    prompt = f"""
    Based on the following content: {final_summary} generate 10-15 questions 
    that will help readers understand the content better then provide
    informative answers to these questions.
    Only give questions that can be answered from the content of the article.
    Provide these answers in the format Question: Answer
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
    SEARCH_ENGINE_ID = "f35b11676565b4fb5"
    url = f"https://www.googleapis.com/customsearch/v1"
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
        else:
            print(results)
    return titles, links