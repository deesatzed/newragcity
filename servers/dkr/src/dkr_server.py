import sys
import os
import json
from pathlib import Path
from typing import Dict, Any, List

from ultrarag.server import UltraRAG_MCP_Server

# Initialize the MCP Server
app = UltraRAG_MCP_Server("dkr-server")

# Global reference to the agent
toc_agent = None

def load_dkr_modules(dkr_root_path: str):
    """Dynamically load DKR modules from the provided path."""
    sys.path.append(dkr_root_path)
    try:
        from src.agents.toc_agent import TOCAgent
        from src.data_loader import DataLoader
        return TOCAgent, DataLoader
    except ImportError as e:
        app.logger.error(f"Failed to load DKR modules from {dkr_root_path}: {e}")
        raise

@app.tool(output="results")
def lookup_exact(query: str, max_chunk_chars: int = 2000) -> Dict[str, Any]:
    """
    Perform a deterministic exact lookup using the DKR TOC Agent.
    
    Args:
        query: The user's specific query.
        max_chunk_chars: Max characters to return before using a pointer.
        
    Returns:
        Dictionary containing ranked list of exact matches.
    """
    global toc_agent
    if not toc_agent:
        return {"error": "DKR Agent not initialized", "results": []}

    app.logger.info(f"DKR Exact Lookup: {query}")
    
    trace = toc_agent.get_routing_trace(query)
    ranked_sections = toc_agent.route_query(query)
    
    results = []
    for file_id, section_id, score, metadata in ranked_sections:
        if score > 10.0:
            content = metadata.get('text', '')
            
            # --- POINTER LOGIC START ---
            if len(content) > max_chunk_chars:
                snippet = content[:max_chunk_chars]
                content = f"{snippet}\n... [TRUNCATED. Full content in {file_id}#{section_id}]"
            # --- POINTER LOGIC END ---

            results.append({
                "file_id": file_id,
                "section_id": section_id,
                "score": score,
                "content": content,
                "source": f"DKR:{file_id}#{section_id}"
            })
            
    return {
        "results": results,
        "trace": trace,
        "count": len(results)
    }

@app.tool(output="status")
def init_agent(dkr_path: str, corpus_path: str) -> Dict[str, str]:
    global toc_agent
    try:
        TOCAgent, DataLoader = load_dkr_modules(dkr_path)
        loader = DataLoader(corpus_path)
        toc = loader.toc
        sections = loader.sections
        toc_agent = TOCAgent(toc, sections)
        app.logger.info(f"DKR Agent initialized with {len(sections)} sections")
        return {"status": "initialized", "sections_loaded": str(len(sections))}
    except Exception as e:
        app.logger.error(f"Initialization failed: {e}")
        return {"status": "failed", "error": str(e)}

if __name__ == "__main__":
    app.run(transport="stdio")