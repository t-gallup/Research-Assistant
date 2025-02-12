from transformers import pipeline
import torch
from google.cloud import storage
import json


def summarize(text):
    # Check GPU availability and setup
    device = 0 if torch.cuda.is_available() else -1
    print(f"Using device: {'cuda' if device == 0 else 'cpu'}")
    
    # Initialize the pipeline with GPU support
    summarizer = pipeline(
        "summarization",
        model="facebook/bart-large-cnn",
        device=device,
        torch_dtype=torch.float16
    )

    # Chunk the text
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
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--text", type=str, required=True)
    # args = parser.parse_args()
    test_text = "Language models (LMs) are enabling researchers to build NLP systems at higher levels of abstraction and with lower data requirements than ever before (Bommasani et al., 2021). This is fueling an exploding space of 'prompting' techniques—and lightweight finetuning techniques—for adapting LMs to new tasks (Kojima et al., 2022), eliciting systematic reasoning from them (Wei et al., 2022; Wanget al., 2022b), and augmenting them with retrieved sources (Guu et al., 2020; Lazaridou et al., 2022; Khattab et al., 2022) or with tools (Yao et al., 2022; Schick et al., 2023). Most of these techniques are explored in isolation, but interest has been growing in building multi-stage pipelines and agents that decompose complex tasks into more manageable calls to LMs in an effort to improve performance (Qi et al., 2019; Khattab et al., 2021a; Karpas et al., 2022; Dohan et al., 2022; Khot et al., 2022; Khattab et al., 2022; Chen et al., 2022; Pourreza & Rafiei, 2023; Shinn et al., 2023). Unfortunately, LMs are known to be sensitive to how they are prompted for each task, and this is exacerbated in pipelines where multiple LM calls have to interact effectively. As a result, the LM 1Preprint calls in existing LM pipelines and in popular developer frameworks are generally implemented using hard-coded 'prompt templates', that is, long strings of instructions and demonstrations that are hand crafted through manual trial and error. We argue that this approach, while pervasive, can be brittle and unscalable—conceptually akin to hand-tuning the weights for a classifier. A given string prompt might not generalize to different pipelines or across different LMs, data domains, or even inputs. Toward a moresystematic approach to designing AI pipelines, we introduce the DSPy programming model.1 DSPy pushes building new LM pipelines away from manipulating free-form strings and closer to programming (composing modular operators to build text transformation graphs) where a compiler automatically generates optimized LM invocation strategies and prompts from a program. Wedraw inspiration from the consensus that emerged around neural network abstractions (Bergstra et al., 2013), where (1) many general-purpose layers can be modularly composed in any complex architecture and (2) the model weights can be trained using optimizers instead of being hand-tuned. To this end, we propose the DSPy programming model (Sec 3). We first translate string-based prompting techniques, including complex and task-dependent ones like Chain of Thought (Wei et al., 2022) and ReAct (Yao et al., 2022), into declarative modules that carry natural-language typed signatures. DSPy modules are task-adaptive components—akin to neural network layers—that abstract any particular text transformation, like answering a question or summarizing a paper. We then parameterize each module so that it can learn its desired behavior by iteratively bootstrapping useful demonstrations within the pipeline. Inspired directly by PyTorch abstractions (Paszke et al., 2019), DSPy modules are used via expressive define-by-run computational graphs. Pipelines are expressed by (1) declaring the modules needed and (2) using these modules in any logical control flow (e.g., if statements, for loops, exceptions, etc.) to logically connect the modules. Wethendevelopthe DSPycompiler(Sec4), whichoptimizesanyDSPyprogramtoimprovequality or cost. The compiler inputs are the program, a few training inputs with optional labels, and a validation metric. The compiler simulates versions of the program on the inputs and bootstraps example traces of each module for self-improvement, using them to construct effective few-shot prompts or finetuning small LMs for steps of the pipeline. Optimization in DSPy is highly modular: it is conducted by teleprompters,2 which are general-purpose optimization strategies that determine how the modules should learn from data. In this way, the compiler automatically maps the declarative modules to high-quality compositions of prompting, finetuning, reasoning, and augmentation. Programming models like DSPy could be assessed along many dimensions, but we focus on the role of expert-crafted prompts in shaping system performance. We are seeking to reduce or even remove their role through DSPy modules (e.g., versions of popular techniques like Chain of Thought) and teleprompters. We report on two expansive case studies: math word problems (GMS8K; Cobbe et al. 2021) and multi-hop question answering (HotPotQA; Yang et al. 2018) with explorations of chain of thought, multi-chain reflection, multi-hop retrieval, retrieval-augmented question answering, and agent loops. Our evaluations use a number of different compiling strategies effectively and show that straightforward DSPy programs outperform systems using hand-crafted prompts, while also allowing our programs to use much smaller and hence more efficient LMs effectively. Overall, this work proposes the first programming model that translates prompting techniques into parameterized declarative modules and introduces an effective compiler with general optimization strategies (teleprompters) to optimize arbitrary pipelines of these modules. Our main contributions are empirical and algorithmic: with DSPy, we have found that we can implement very short programs that can bootstrap self-improving multi-stage NLP systems using LMs as small as llama2-13b-chat and T5-Large (770M parameters). Without hand-crafted prompts and within minutes to tens of minutes of compiling, compositions of DSPy modules can raise the quality of simple programs from 33% to 82% (Sec 6) and from 32% to 46% (Sec 7) for GPT-3.5 and, similarly, from 9% to 47% (Sec 6) and from 22% to 41% (Sec 7) for llama2-13b-chat."
    summary = summarize(test_text)

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
