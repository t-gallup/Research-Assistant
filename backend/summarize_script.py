from transformers import pipeline
import argparse
import json
from google.cloud import storage


def summarize(text):
    summarizer = pipeline(
        "summarization",
        model="facebook/bart-large-cnn",
        device=0  # Use GPU
    )

    max_chunk_size = 1024
    chunks = [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]

    summaries = []
    for chunk in chunks:
        summary = summarizer(
            chunk,
            max_length=130,
            min_length=30,
            do_sample=False
        )
        summaries.append(summary[0]['summary_text'])

    return " ".join(summaries)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", type=str, required=True)
    args = parser.parse_args()

    summary = summarize(args.text)

    storage_client = storage.Client()
    bucket_name = "summarizationbucket"
    bucket = storage_client.bucket(bucket_name)

    # Save summary to GCS
    blob = bucket.blob('summary.json')
    blob.upload_from_string(
        json.dumps({"summary": summary}),
        content_type='application/json'
    )


if __name__ == "__main__":
    main()
