#!/usr/bin/env python3
"""
Download BEIR nfcorpus dataset for DKR benchmarking.

NFCorpus is a small medical/nutrition-focused dataset, perfect for testing
DKR's medical knowledge retrieval capabilities.
"""

import os
from pathlib import Path
from beir import util
from beir.datasets.data_loader import GenericDataLoader


def download_nfcorpus():
    """Download BEIR nfcorpus dataset."""

    # Set download directory
    data_dir = Path(__file__).parent / "datasets"
    data_dir.mkdir(exist_ok=True)

    dataset = "nfcorpus"

    print("="*70)
    print(f"Downloading BEIR dataset: {dataset}")
    print("="*70)
    print()

    # Download dataset
    url = f"https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/{dataset}.zip"
    out_dir = str(data_dir)

    print(f"Dataset: {dataset}")
    print(f"URL: {url}")
    print(f"Output directory: {out_dir}")
    print()

    data_path = util.download_and_unzip(url, out_dir)

    print()
    print("="*70)
    print("Download Complete!")
    print("="*70)
    print(f"Dataset location: {data_path}")
    print()

    # Load and inspect dataset
    print("Loading dataset to verify...")
    corpus, queries, qrels = GenericDataLoader(data_folder=data_path).load(split="test")

    print()
    print("Dataset Statistics:")
    print(f"  Corpus size:  {len(corpus):,} documents")
    print(f"  Query count:  {len(queries):,} queries")
    print(f"  Relevance judgments: {sum(len(v) for v in qrels.values()):,}")
    print()

    # Show sample query
    sample_query_id = list(queries.keys())[0]
    sample_query = queries[sample_query_id]
    print("Sample Query:")
    print(f"  ID: {sample_query_id}")
    print(f"  Text: {sample_query}")
    print()

    # Show sample document
    sample_doc_id = list(corpus.keys())[0]
    sample_doc = corpus[sample_doc_id]
    print("Sample Document:")
    print(f"  ID: {sample_doc_id}")
    print(f"  Title: {sample_doc.get('title', 'N/A')}")
    print(f"  Text (first 200 chars): {sample_doc.get('text', 'N/A')[:200]}...")
    print()

    print("="*70)
    print("✓ BEIR nfcorpus dataset ready for benchmarking")
    print("="*70)

    return data_path


if __name__ == '__main__':
    download_nfcorpus()
