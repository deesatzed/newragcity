#!/opt/homebrew/anaconda3/envs/py13/bin/python

import asyncio

from pathlib import Path

import sys

sys.path.append('/Volumes/WS4TB/ERSATZ_RAG/regulus/backend')

from app.indexing import IndexingService

def main():

    ws_ed_path = Path("/Volumes/WS4TB/ERSATZ_RAG/WS_ED")

    pdfs = list(ws_ed_path.glob("*.pdf"))

    if not pdfs:

        print("No PDFs found in WS_ED")

        return

    service = IndexingService()

    asyncio.run(service.run_indexing(pdfs))

    print(f"Indexed {len(pdfs)} PDFs from WS_ED")

if __name__ == "__main__":

    main()
