import argparse
import json
import os
from pathlib import Path
from typing import Dict, Any, List
from tqdm import tqdm

# Lazy import handling for proof-of-life without full venv
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None
    print("Warning: PyMuPDF (fitz) not found. PDF processing will be skipped. Run 'uv sync' to enable.")

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract high-quality text from PDF using PyMuPDF.
    """
    if not fitz:
        return ""
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text

def extract_text_from_file(file_path: Path) -> str:
    if file_path.suffix.lower() == ".pdf":
        return extract_text_from_pdf(str(file_path))
    elif file_path.suffix.lower() in [".txt", ".md", ".json", ".py", ".yaml"]:
        try:
            return file_path.read_text(encoding="utf-8")
        except Exception as e:
             print(f"Error reading {file_path}: {e}")
             return ""
    return ""

def update_dkr_corpus(entries: List[Dict[str, Any]], corpus_path: str):
    """
    Append list of entries to the JSONL corpus used by DKR.
    """
    # We append if file exists, or write new if not, to respect existing data in a real usage
    # But for this bulk script, we might want to overwrite or dedup. 
    # For proof of life, we overwrite to be clean.
    with open(corpus_path, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")

def main():
    parser = argparse.ArgumentParser(description="Bulk Ingestion Engine for The Vault")
    parser.add_argument("--input_dir", default="TheVault/data/input_docs", help="Directory containing raw documents")
    parser.add_argument("--corpus", default="TheVault/data/corpus.jsonl", help="DKR corpus output path")
    
    args = parser.parse_args()
    
    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        print(f"Input directory not found: {input_dir}")
        return

    files = [f for f in input_dir.rglob("*") if f.is_file() and not f.name.startswith(".")]
    
    print(f"Found {len(files)} files to ingest from {input_dir}...")
    
    dkr_entries = []
    
    # Simple iterator if tqdm is missing
    iterator = files
    try:
        iterator = tqdm(files, desc="Processing files")
    except NameError:
        pass
    
    for file_path in iterator:
        content = extract_text_from_file(file_path)
        
        if not content.strip():
            continue
            
        metadata = {
            "file_id": file_path.stem,
            "title": file_path.name
        }
        
        entry = {
            "file_id": metadata["file_id"],
            "section_id": "root", 
            "text": content,
            "label": metadata["title"],
            "aliases": [metadata["title"]],
            "entities": []
        }
        dkr_entries.append(entry)
    
    output_path = Path(args.corpus)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    update_dkr_corpus(dkr_entries, str(output_path))
    
    print(f"Ingestion complete. {len(dkr_entries)} documents added to {args.corpus}")

if __name__ == "__main__":
    main()