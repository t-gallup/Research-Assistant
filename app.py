import streamlit as st
import faq_pipeline as fp
import asyncio
import warnings
import importlib

warnings.filterwarnings("ignore")
importlib.reload(fp)

def set_url(url):
    st.session_state.url_input = url

st.set_page_config(page_title="FAQ Generator",
                    page_icon="faq-logo.png"
)
st.cache_data.clear()
st.title("FAQ Generator")

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

url = st.text_input("Enter website URL to generate an FAQ for:", key='url_input')
async def generate_faq(url):
    status_text = st.empty()
    progress_bar = st.progress(0)

    status_text.text("Loading website content...")
    html = await fp.load_html(url)
    doc_string, article_title = fp.extract_from_html(html)
    progress_bar.progress(33)

    status_text.text("Summarizing content...")
    final_summary = fp.summarize_content(doc_string)
    progress_bar.progress(66)

    status_text.text("Generating FAQ...")
    topic_list = fp.prompt_llm_for_related_topics(final_summary)
    rec_titles, rec_links = [], []
    results = fp.search_google(topic_list[0])
    new_rec_titles, new_rec_links = fp.get_top_5_articles(results, url)
    rec_titles += new_rec_titles
    rec_links += new_rec_links
    questions, answers = fp.prompt_llm(final_summary)
    
    results = fp.search_google(topic_list[1])
    new_rec_titles, new_rec_links = fp.get_top_5_articles(results, url)
    rec_titles += new_rec_titles
    rec_links += new_rec_links

    progress_bar.progress(100)

    status_text.text("FAQ generation complete...")
    st.markdown(f"## {article_title}")
    for i in range(len(questions)):
        expand_faq = st.expander(questions[i])
        with expand_faq:
            st.write(answers[i])
    st.write(f"Article Summary: {final_summary}")
    
    # for topic in topic_list:
    #     results = fp.search_google(topic)
    #     new_rec_titles, new_rec_links = fp.get_top_5_articles(results, url)
    #     rec_titles += new_rec_titles
    #     rec_links += new_rec_links
        # print(topic)
    # print(topic_list)
    
    st.sidebar.header("Recommended Articles")
    for i, title in enumerate(rec_titles):
        if st.sidebar.button(title, key=i, on_click=set_url, args=(rec_links[i],)):
            # set_url(rec_links[i])
            generate_faq(rec_links[i])
    # st.sidebar.selectbox("Choose an article: ", rec_titles)

if url:
    # with st.spinner("Generating FAQ..."):
    asyncio.run(generate_faq(url))