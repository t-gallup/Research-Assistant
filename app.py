import streamlit as st
from faq_pipeline import *
import asyncio

st.set_page_config(page_title="FAQ Generator",
                    page_icon="faq-logo.png"
)

st.title("FAQ Generator")

url = st.text_input("Enter website URL to generate an FAQ for")
async def generate_faq(url):
    html = await load_html(url)
    doc_string = extract_from_html(html)
    final_summary = summarize_content(doc_string)
    questions, answers = prompt_llm(final_summary)
    for i in range(len(questions)):
        expand_faq = st.expander(questions[i])
        with expand_faq:
            st.write(answers[i])
if url:
    asyncio.run(generate_faq(url))