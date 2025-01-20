import os
import io
import math
import requests
import azure.cognitiveservices.speech as speechsdk
from PyPDF2 import PdfReader
from openai import OpenAI
import openai
from tqdm import tqdm
from pydub import AudioSegment
from dotenv import load_dotenv

load_dotenv()

class PDFAudioSummarizer:
    def __init__(self, openai_api_key, azure_key, azure_region):
        self.openai_api_key = openai_api_key
        self.azure_key = azure_key
        self.azure_region = azure_region
        openai.api_key = openai_api_key
        
    def download_pdf(self, url):
        """Download PDF from URL"""
        response = requests.get(url)
        return io.BytesIO(response.content)

    def extract_text_with_chunks(self, pdf_file, chunk_size=4000):
        """Extract text from PDF and split into chunks"""
        reader = PdfReader(pdf_file)
        chunks = []
        current_chunk = ""
        
        for page in reader.pages:
            text = page.extract_text()
            words = text.split()
            
            for word in words:
                if len(current_chunk) + len(word) + 1 <= chunk_size:
                    current_chunk += word + " "
                else:
                    chunks.append(current_chunk.strip())
                    current_chunk = word + " "
                    
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks

    def summarize_chunk(self, chunk):
        """Generate summary for a single chunk using OpenAI"""
        client = OpenAI()
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Create a concise summary \
                     of the following text, maintaining key information \
                     and context:"},
                    {"role": "user", "content": chunk}
                ],
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error summarizing chunk: {str(e)}")
            return ""

    def generate_final_summary(self, chunk_summaries):
        """Generate final cohesive summary from all chunk summaries"""
        combined_summary = "\n\n".join(chunk_summaries)
        client = OpenAI()
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Create a well-structured \
                    3-5 minute spoken summary from these section summaries. \
                     Make it flow naturally for audio listening:"},
                    {"role": "user", "content": combined_summary}
                ],
                max_tokens=1500
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating final summary: {str(e)}")
            return ""

    def text_to_speech_azure(self, text, output_file):
        """Convert text to speech using Azure"""
        speech_config = speechsdk.SpeechConfig(
            subscription=self.azure_key,
            region=self.azure_region
        )
        
        # Configure voice
        speech_config.speech_synthesis_voice_name = "en-US-JennyMultilingualNeural"
        
        audio_config = speechsdk.AudioOutputConfig(filename=output_file)
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config
        )
        
        result = synthesizer.speak_text_async(text).get()
        
        if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
            raise Exception(f"Speech synthesis failed: {result.reason}")

    def process_pdf(self, url, output_file="summary.mp3"):
        """Main processing pipeline"""
        try:
            print("Downloading PDF...")
            pdf_file = self.download_pdf(url)
            
            print("Extracting text in chunks...")
            chunks = self.extract_text_with_chunks(pdf_file)
            
            print(f"Summarizing {len(chunks)} chunks...")
            chunk_summaries = []
            for i, chunk in enumerate(tqdm(chunks)):
                summary = self.summarize_chunk(chunk)
                if summary:
                    chunk_summaries.append(summary)
            
            print("Generating final summary...")
            final_summary = self.generate_final_summary(chunk_summaries)
            
            print("Converting to speech...")
            self.text_to_speech_azure(final_summary, output_file)
            
            print(f"Summary audio saved to {output_file}")
            return True
            
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            return False


# Usage example
if __name__ == "__main__":
    # Initialize with your API keys
    summarizer = PDFAudioSummarizer(
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        azure_key=os.getenv('AZURE_SPEECH_KEY'),
        azure_region="uswest2"
    )

    # Process a PDF
    url = "https://arxiv.org/pdf/2310.03714"
    summarizer.process_pdf(url, "dspy.mp3")
