import streamlit as st
from faq_pipeline import *
import asyncio
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="FAQ Generator",
                    page_icon="faq-logo.png"
)

st.title("FAQ Generator")

st.markdown("""
    <style>
    input[type="text"] {
        font-size: 16px !important;
    }
    p {
        font-size: 20px !important;
    }
    div {
        font-size: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

url = st.text_input("Enter website URL to generate an FAQ for:")
async def generate_faq(url):
    status_text = st.empty()
    progress_bar = st.progress(0)

    status_text.text("Loading website content...")
    html = await load_html(url)
    doc_string = extract_from_html(html)
    progress_bar.progress(33)

    status_text.text("Summarizing content...")
    final_summary = summarize_content(doc_string)
    progress_bar.progress(66)

    status_text.text("Generating FAQ...")
    questions, answers = prompt_llm(final_summary)
    progress_bar.progress(100)

    status_text.text("FAQ generation complete...")
    for i in range(len(questions)):
        expand_faq = st.expander(questions[i])
        with expand_faq:
            st.write(answers[i])
if url:
    # with st.spinner("Generating FAQ..."):
    asyncio.run(generate_faq(url))