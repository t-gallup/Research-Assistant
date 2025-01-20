# Add at the top of the file
import torch
from transformers import pipeline
import tensorflow as tf


# Update the summarize_content function to better handle GPU
def summarize_content(doc_string):
    # Check for GPU availability
    if torch.cuda.is_available():
        logger.info("GPU detected, using PyTorch GPU")
        device = 0
    else:
        logger.info("No GPU detected, using CPU")
        device = -1
        
    summarizer = pipeline(
        "summarization",
        model="facebook/bart-large-cnn",
        device=device
    )
    

    # Rest of the function remains the same
    max_chunk_size = 1000
    inputs = summarizer.tokenizer(doc_string, return_tensors="pt",
                                  truncation=False)
    tokens = inputs.input_ids[0]
    chunks = [tokens[i:i+max_chunk_size] for i in range(0, len(tokens),
                                                        max_chunk_size)]
    batch_chunk_texts = [summarizer.tokenizer.decode(chunk, 
                                    skip_special_tokens=True) for chunk in chunks]
    summaries = summarizer(batch_chunk_texts, max_length=100, truncation=True)
    summary_texts = [summary['summary_text'] for summary in summaries]
    final_summary = " ".join(summary_texts)
    return final_summary
