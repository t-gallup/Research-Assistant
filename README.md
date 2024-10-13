**Q&A Generator: Summarize and Explore Web Content with Ease**

Inspired by Google's People Also Ask section, the Q&A Generator is a project to help summarize content from any website into informative questions and answers along with a concise summary of the article. After providing this clarity for the website you choose, the app also generates a list of related articles that you can explore in the same way. This makes it easy to quickly do a deep dive into any topic you want to learn about!

Steps for running Q&A Generator App:
1. Clone the repository:
    ```bash
    git clone https://github.com/t-gallup/QnA-Generator.git
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Set your API keys:
    ```bash
    export OPENAI_API_KEY='your-openai-key'
    export GOOGLE_API_KEY='your-google-key'
    export SEARCH_ENGINE_ID='your-search-engine-id'
    ```

4. Run the Streamlit app:
    ```bash
    streamlit run app.py
    ```
