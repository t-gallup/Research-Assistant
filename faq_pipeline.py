from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
from transformers import pipeline
import openai
import re

async def load_html(url):
    print(url)
    loader = AsyncHtmlLoader(url)
    html = loader.load()
    return html

def extract_from_html(html):
    bs_transformer = BeautifulSoupTransformer()
    docs_transformed = bs_transformer.transform_documents(html, tags_to_extract=["span"])
    doc_string = ""
    for doc in docs_transformed:
        doc_string += doc.page_content
    return doc_string

def summarize_content(doc_string):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device="cpu")
    max_chunk_size = 1000
    inputs = summarizer.tokenizer(doc_string, return_tensors="pt", truncation=False, clean_up_tokenization_space=True)
    tokens = inputs.input_ids[0]
    chunks = [tokens[i:i+max_chunk_size] for i in range(0, len(tokens), max_chunk_size)]
    summaries = []
    for chunk in chunks:
        chunk_text = summarizer.tokenizer.decode(chunk, skip_special_tokens=True)
        summary = summarizer(chunk_text, max_length=1000, truncation=True)[0]['summary_text']
        summaries.append(summary)
    final_summary = " ".join(summaries)
    return final_summary

def prompt_llm(final_summary):
    prompt = f"""
    Based on the following content: {final_summary} generate 10-15 questions 
    that will help readers understand the content better then provide
    informative answers to these questions.
    Provide these answers in the format Question: Answer
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