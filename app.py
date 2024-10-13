import streamlit as st
import rag_pipeline as rp
import asyncio
import warnings
import importlib

warnings.filterwarnings("ignore")
importlib.reload(rp)

def set_url(url):
    st.session_state.url_input = url

st.set_page_config(page_title="Q&A Generator",
                    page_icon="images/qa-logo.png"
)
st.cache_data.clear()
st.title("Q&A Generator")

st.markdown("""
    <style>
    input[type="text"] {
        font-size: 14px !important;
    }
    label[for="url_input"] {
        font-size: 20px !important;
    }
    div {
        font-size: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

url = st.text_input("Enter website URL to learn about:", key='url_input')
async def generate_faq(url):
    status_text = st.empty()
    progress_bar = st.progress(0)

    status_text.text("Loading website content...")
    file_type = rp.check_file_type(url)
    doc_string, article_title = "", ""
    if file_type == "html":
        html = await rp.load_html(url)
        doc_string, article_title = rp.extract_from_html(html)
    elif file_type == "pdf":
        pdf, response = rp.load_pdf(url)
        doc_string, article_title = rp.extract_from_pdf(pdf, response)
    # else:

    progress_bar.progress(33)

    status_text.text("Summarizing content...")
    final_summary = rp.summarize_content(doc_string)
    progress_bar.progress(66)

    status_text.text("Generating Q&A...")
    topic_list = rp.prompt_llm_for_related_topics(final_summary)
    rec_titles, rec_links = [], []
    results = rp.search_google(topic_list[0])
    new_rec_titles, new_rec_links = rp.get_top_5_articles(results, url)
    rec_titles += new_rec_titles
    rec_links += new_rec_links
    questions, answers = rp.prompt_llm(final_summary)
    
    results = rp.search_google(topic_list[1])
    new_rec_titles, new_rec_links = rp.get_top_5_articles(results, url)
    rec_titles += new_rec_titles
    rec_links += new_rec_links

    progress_bar.progress(100)

    status_text.text("Q&A generation complete...")
    if article_title != "":
        st.markdown(f"## {article_title}")
    for i in range(min(len(questions), len(answers))):
        expand_faq = st.expander(questions[i])
        with expand_faq:
            st.write(answers[i])
    st.write(f"Article Summary: {final_summary}")
    
    st.sidebar.header("Recommended Articles")
    for i, title in enumerate(rec_titles):
        if st.sidebar.button(title, key=i, on_click=set_url, args=(rec_links[i],)):
            generate_faq(rec_links[i])

if url:
    asyncio.run(generate_faq(url))