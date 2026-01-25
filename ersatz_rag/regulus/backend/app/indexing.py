from pathlib import Path
from typing import List

from leann.api import LeannBuilder
from leann.registry import autodiscover_backends
try:
    from pageindex import page_index_main  # type: ignore
except Exception:
    page_index_main = None  # Fallback will be used

from .config import (
    EMBEDDING_MODEL, 
    LEANN_BACKEND, 
    LEANN_EMBEDDING_MODE,
    INDEX_PATH,
    DEFAULT_METADATA,
    get_embedding_model,
    get_index_path
)

# Discover backends when the module is loaded
autodiscover_backends()

def process_pdf(pdf_path: str) -> dict:
    """
    Process PDF using PageIndex to generate hierarchical structure
    """
    try:
        # Use PageIndex to get the tree structure if available
        if page_index_main is not None:
            tree_structure = page_index_main(pdf_path)
            return {"nodes": tree_structure}
        raise RuntimeError("PageIndex not available")
    except Exception as e:
        # Fallback to simple page-by-page processing if PageIndex fails
        print(f"PageIndex failed, falling back to simple processing: {e}")
        import fitz
        nodes = []
        doc = fitz.open(pdf_path)
        for i, page in enumerate(doc):
            text = page.get_text()
            nodes.append({
                "node_id": f"{Path(pdf_path).stem}_{i}",
                "title": f"Page {i+1}",
                "content": text,
                "summary": text[:200],
                "page_ranges": [i+1, i+1]
            })
        doc.close()
        return {"nodes": nodes}

class IndexingService:

    def __init__(self, embedding_model: str = None):
        """
        Initialize IndexingService with configurable embedding model
        
        Args:
            embedding_model: Override embedding model (defaults to config)
        """
        model = get_embedding_model(embedding_model) if embedding_model else EMBEDDING_MODEL
        
        self.embedding_model = model
        self.builder = LeannBuilder(
            backend_name=LEANN_BACKEND,
            embedding_model=model,
            embedding_mode=LEANN_EMBEDDING_MODE
        )
        
        print(f"IndexingService initialized with embedding model: {model}")

    async def run_indexing(self, paths: List[Path]):
        for path in paths:
            if path.suffix == '.pdf':
                tree = process_pdf(str(path))
                for node in tree['nodes']:
                    # Extract content from PageIndex node structure
                    if isinstance(node, dict):
                        content = node.get('content', '') or node.get('text', '')
                        title = node.get('title', '')
                        summary = node.get('summary', '')
                        node_id = node.get('node_id', '')
                        
                        # Create combined text for embedding
                        chunk_text = f"{title} {summary} {content}".strip()
                        
                        # Start with default metadata and override with specific values
                        doc_metadata = DEFAULT_METADATA.copy()
                        doc_metadata.update({
                            'node_id': node_id,
                            'title': title,
                            'source_file': str(path.name),
                            'embedding_model': self.embedding_model
                        })
                        
                        # Add page ranges if available
                        if 'page_ranges' in node:
                            doc_metadata['page_ranges'] = node['page_ranges']
                            
                        self.builder.add_text(chunk_text, metadata=doc_metadata)

        # Generate index path with embedding model suffix for clarity
        model_suffix = self.embedding_model.split("/")[-1].replace("-", "_")
        index_path = get_index_path(model_suffix)
        
        self.builder.build_index(index_path)
        print(f"Index built with {self.embedding_model} at: {index_path}")
        return index_path
