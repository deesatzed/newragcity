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
def lookup_exact(query: str) -> Dict[str, Any]:
    """
    Perform a deterministic exact lookup using the DKR TOC Agent.
    
    Args:
        query: The user's specific query (e.g. "Error 505", "Policy 1.2")
        
    Returns:
        Dictionary containing ranked list of exact matches.
    """
    global toc_agent
    if not toc_agent:
        return {"error": "DKR Agent not initialized", "results": []}

    app.logger.info(f"DKR Exact Lookup: {query}")
    
    # Get routing trace for explainability
    trace = toc_agent.get_routing_trace(query)
    
    # Get ranked results
    ranked_sections = toc_agent.route_query(query)
    
    results = []
    for file_id, section_id, score, metadata in ranked_sections:
        # Only include high-scoring exact matches (heuristic threshold)
        if score > 10.0:  # Threshold assumes text hits(2) + alias hits(3)
            results.append({
                "file_id": file_id,
                "section_id": section_id,
                "score": score,
                "content": metadata.get('text', ''),
                "source": f"DKR:{file_id}#{section_id}"
            })
            
    return {
        "results": results,
        "trace": trace,
        "count": len(results)
    }

@app.tool(output="status")
def init_agent(dkr_path: str, corpus_path: str) -> Dict[str, str]:
    """
    Initialize the DKR Agent.
    
    Args:
        dkr_path: Path to the root of the DKR repository.
        corpus_path: Path to the JSONL corpus directory.
    """
    global toc_agent
    try:
        TOCAgent, DataLoader = load_dkr_modules(dkr_path)
        
        # Load Data
        loader = DataLoader(corpus_path)
        toc = loader.toc
        sections = loader.sections
        
        # Initialize Agent
        toc_agent = TOCAgent(toc, sections)
        app.logger.info(f"DKR Agent initialized with {len(sections)} sections")
        return {"status": "initialized", "sections_loaded": str(len(sections))}
    except Exception as e:
        app.logger.error(f"Initialization failed: {e}")
        return {"status": "failed", "error": str(e)}

if __name__ == "__main__":
    app.run(transport="stdio")
