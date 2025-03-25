# import os
# import io
# import requests
# import azure.cognitiveservices.speech as speechsdk
# from PyPDF2 import PdfReader
# from openai import OpenAI
# import openai
# from tqdm import tqdm
# from dotenv import load_dotenv
# import logging
# from bs4 import BeautifulSoup
# import httpx
# from google import genai

# load_dotenv()

# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S'
# )
# logger = logging.getLogger(__name__)


# class PDFAudioSummarizer:
#     def __init__(self, openai_api_key, azure_key, azure_region):
#         self.openai_api_key = openai_api_key
#         self.azure_key = azure_key
#         self.azure_region = azure_region
#         openai.api_key = openai_api_key

#     def download_pdf(self, url):
#         """Download PDF from URL"""
#         response = requests.get(url)
#         return io.BytesIO(response.content)

#     def extract_pdf_with_chunks(self, pdf_file):
#         """Extract text from PDF and split into one chunk per page"""
#         reader = PdfReader(pdf_file)
#         chunks = []

#         for page_num, page in enumerate(reader.pages, 1):
#             logger.debug(f"Processing PDF page {page_num}")
#             text = page.extract_text()
            
#             if not text or text.isspace():
#                 logger.debug(f"Page {page_num} is empty or whitespace")
#                 continue

#             # Clean the text
#             cleaned_text = "".join(c for c in text if ord(c) < 128)
#             cleaned_text = ' '.join(cleaned_text.split())
            
#             if cleaned_text.strip():
#                 logger.debug(f"Page {page_num} cleaned text sample: {cleaned_text[:100]}")
#                 chunks.append({
#                     'page': page_num,
#                     'text': cleaned_text.strip()
#                 })

#         logger.debug(f"Extracted {len(chunks)} pages with content")
#         return chunks

#     def download_html(self, url):
#         """Download HTML from URL"""
#         response = requests.get(url)
#         return response.text

#     def extract_html_with_chunks(self, html_content, chunk_size=16000):
#         """Extract text from HTML and split into chunks"""
#         soup = BeautifulSoup(html_content, 'html.parser')

#         for script_or_style in soup(['script', 'style']):
#             script_or_style.decompose()

#         text = ' '.join(soup.get_text().split())

#         text = text.replace('\x00', '')
#         cleaned_text = ""
#         for c in text:
#             if ord(c) < 128:
#                 cleaned_text += c

#         cleaned_text = ' '.join(cleaned_text.split())

#         logger.debug(f"Cleaned text sample: {cleaned_text[:100]}...")

#         chunks = []
#         current_chunk = ""
#         words = cleaned_text.split()

#         for word in words:
#             if len(current_chunk) + len(word) + 1 <= chunk_size:
#                 current_chunk += word + " "
#             else:
#                 chunks.append(current_chunk.strip())
#                 current_chunk = word + " "

#         if current_chunk:
#             chunks.append(current_chunk.strip())

#         return chunks

#     def summarize_chunk(self, chunk):
#         """Generate summary for a single chunk using OpenAI"""
#         client = genai.Client()
#         try:

#             prompt = f"""Please create a concise summary of the following text, focusing on key information:

#             Text to summarize:
#             {chunk}

#             Summary:"""
#             response = client.models.generate_content(
#                 model="gemini-1.5-flash",
#                 contents=[{
#                     "role": "user",
#                     "parts": [{"text": prompt}]
#                 }])
#             # response = client.chat.completions.create(
#             #     model="gpt-3.5-turbo",
#             #     messages=[
#             #         {"role": "system", "content": "Create a concise summary \
#             #          of the following text, maintaining key information \
#             #          and context:"},
#             #         {"role": "user", "content": chunk}
#             #     ],
#             #     max_tokens=1000
#             # )
#             if response.candidates and response.candidates[0].content:
#                 return response.candidates[0].content.parts[0].text
#             else:
#                 logger.error("No valid response generated")
#             return ""
#         except Exception as e:
#             logging.error(f"Error summarizing chunk: {str(e)}")
#             return ""

#     def generate_final_summary(self, chunk_summaries):
#         """Generate final cohesive summary from all chunk summaries"""
#         combined_summary = "\n\n".join(chunk_summaries)
#         client = OpenAI()
#         try:
#             response = client.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "system", "content": "Create a well-structured \
#                     3-5 minute spoken summary from these section summaries. \
#                      Make it flow naturally for audio listening:"},
#                     {"role": "user", "content": combined_summary}
#                 ],
#                 max_tokens=1500
#             )
#             return response.choices[0].message.content
#         except Exception as e:
#             logging.error(f"Error generating final summary: {str(e)}")
#             return ""

#     def text_to_speech_azure(self, text, output_file):
#         """Convert text to speech using Azure"""
#         speech_config = speechsdk.SpeechConfig(
#             subscription=self.azure_key,
#             region=self.azure_region
#         )

#         speech_config.speech_synthesis_voice_name = "en-US-BrianMultilingualNeural"
#         audio_config = speechsdk.audio.AudioConfig(filename=output_file)
#         synthesizer = speechsdk.SpeechSynthesizer(
#             speech_config=speech_config,
#             audio_config=audio_config
#         )

#         result = synthesizer.speak_text_async(text).get()

#         if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
#             raise Exception(f"Speech synthesis failed: {result.reason}")

#     def process_file(self, url, output_file="summary.mp3"):
#         try:
#             doc_data = httpx.get(url)
#             content_type = doc_data.headers.get('content-type', '').lower()
            
#             logger.debug(f"Content type detected: {content_type}")
#             chunks = []

#             if 'application/pdf' in content_type:
#                 logger.debug("Processing as PDF...")
#                 pdf_file = io.BytesIO(doc_data.content)
#                 chunks = self.extract_pdf_with_chunks(pdf_file)
#                 chunk_summaries = []
#                 for chunk in tqdm(chunks):
#                     summary_text = self.summarize_chunk(chunk['text'])
#                     if summary_text:
#                         chunk_summaries.append({
#                             "page": chunk['page'],
#                             "summary": summary_text
#                         })
            
#             elif 'text/html' in content_type:
#                 logger.debug("Processing as HTML...")
#                 html_content = doc_data.text
#                 chunks = self.extract_html_with_chunks(html_content)
#                 chunk_summaries = []
#                 for i, chunk in enumerate(tqdm(chunks), 1):
#                     summary_text = self.summarize_chunk(chunk)
#                     if summary_text:
#                         chunk_summaries.append({
#                             "page": i,
#                             "summary": summary_text
#                         })
#             else:
#                 logger.error(f"Unsupported content type: {content_type}")
#                 return {"success": False, "error": "Unsupported file type"}

#             if not chunk_summaries:
#                 logger.warning("No valid summaries were generated")
#                 return {"success": False, "error": "No summaries generated", "chunk_summaries": []}

#             final_summary = self.generate_final_summary([s["summary"] for s in chunk_summaries])
            
#             logger.debug("Converting to speech...")
#             self.text_to_speech_azure(final_summary, output_file)

#             logger.debug(f"Summary audio saved to {output_file}")
#             return {
#                 "success": True,
#                 "chunk_summaries": chunk_summaries,
#                 "final_summary": final_summary,
#                 "audio_file": os.path.basename(output_file)
#             }

#         except Exception as e:
#             logger.error(f"Error processing file: {str(e)}")
#             return {"success": False, "error": str(e), "chunk_summaries": []}

# # Usage example
# if __name__ == "__main__":
#     summarizer = PDFAudioSummarizer(
#         openai_api_key=os.getenv('OPENAI_API_KEY'),
#         azure_key=os.getenv('AZURE_SPEECH_KEY'),
#         azure_region="westus2"
#     )