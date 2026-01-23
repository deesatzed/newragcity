import json
import random
import asyncio
import os
import argparse
from pathlib import Path
from typing import List, Dict, Any

# We reuse the local_llm server logic or client directly
from openai import AsyncOpenAI

async def generate_qa_pair(client: AsyncOpenAI, model: str, text_chunk: str, source_id: str) -> Dict[str, Any]:
    """
    Ask the LLM to generate a question based on the text.
    """
    prompt = f"""
    You are an expert examiner. Read the following text and create a specific question that can ONLY be answered using this text.
    Also provide the correct answer and cite the Source ID.
    
    Text: "{text_chunk[:1500]}"
    Source ID: {source_id}
    
    Format your response as valid JSON:
    {{
        "question": "The question text",
        "answer": "The answer text",
        "citation": "{source_id}"
    }}
    """
    
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        content = response.choices[0].message.content
        # Basic cleanup to find JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
             content = content.split("```")[1].split("```")[0]
             
        return json.loads(content)
    except Exception as e:
        print(f"Error generating Q/A: {e}")
        return None

async def main():
    parser = argparse.ArgumentParser(description="Generate Synthetic Golden Set for Evaluation")
    parser.add_argument("--corpus", default="TheVault/data/corpus.jsonl", help="Path to corpus")
    parser.add_argument("--output", default="TheVault/data/golden_set.json", help="Output path")
    parser.add_argument("--samples", type=int, default=10, help="Number of test cases to generate")
    parser.add_argument("--base_url", default="http://localhost:8000/v1", help="Local LLM URL")
    parser.add_argument("--model", default="qwen2.5-14b-instruct", help="Model name")
    
    args = parser.parse_args()
    
    corpus_path = Path(args.corpus)
    if not corpus_path.exists():
        print("Corpus not found. Run ingest_bulk.py first.")
        return

    # Load corpus
    docs = []
    with open(corpus_path, "r") as f:
        for line in f:
            docs.append(json.loads(line))
            
    if not docs:
        print("Corpus is empty.")
        return

    # Initialize Client
    client = AsyncOpenAI(base_url=args.base_url, api_key="EMPTY")
    
    # Select random docs
    selected_docs = random.sample(docs, min(len(docs), args.samples))
    
    golden_set = []
    print(f"Generating {len(selected_docs)} Q/A pairs using {args.model}...")
    
    for doc in selected_docs:
        qa = await generate_qa_pair(client, args.model, doc['text'], doc['file_id'])
        if qa:
            qa['source_file'] = doc['file_id']
            golden_set.append(qa)
            print(f"Generated: {qa['question']}")
            
    # Save Golden Set
    with open(args.output, "w") as f:
        json.dump(golden_set, f, indent=2)
        
    print(f"Golden set saved to {args.output}")

if __name__ == "__main__":
    asyncio.run(main())
