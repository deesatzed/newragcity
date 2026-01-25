import sys
import asyncio
from pathlib import Path
from typing import Dict, Any

from ultrarag.server import UltraRAG_MCP_Server

app = UltraRAG_MCP_Server("ersatz-server")

cognitron_agent = None

def load_ersatz_modules(ersatz_root_path: str):
    """Dynamically load Ersatz/Cognitron modules."""
    sys.path.append(ersatz_root_path)
    try:
        from cognitron.core.agent import CognitronAgent
        return CognitronAgent
    except ImportError as e:
        app.logger.error(f"Failed to load Ersatz modules from {ersatz_root_path}: {e}")
        raise

@app.tool(output="answer,confidence,chunks")
async def semantic_search(query: str, threshold: float = 0.80, max_chunk_chars: int = 2000) -> Dict[str, Any]:
    """
    Perform semantic search with confidence gating using Ersatz.
    
    Args:
        query: User query.
        threshold: Minimum confidence score (0.0 - 1.0).
        max_chunk_chars: Max characters to return before using a pointer.
        
    Returns:
        Dict with answer, confidence score, and source chunks.
    """
    global cognitron_agent
    if not cognitron_agent:
        return {"error": "Ersatz Agent not initialized", "confidence": 0.0}

    app.logger.info(f"Ersatz Semantic Search: {query} (Threshold: {threshold})")
    
    result = await cognitron_agent.ask(
        query=query,
        require_high_confidence=True
    )
    
    chunks = []
    if result.relevant_chunks:
        for chunk in result.relevant_chunks:
            
            content = chunk.content
            # --- POINTER LOGIC START ---
            if len(content) > max_chunk_chars:
                snippet = content[:max_chunk_chars]
                content = f"{snippet}\n... [TRUNCATED. Full content in {chunk.source_id}]"
            # --- POINTER LOGIC END ---

            chunks.append({
                "title": chunk.title,
                "content": content,
                "confidence": chunk.confidence_score,
                "source": f"Ersatz:{chunk.source_id}"
            })
            
    final_answer = result.answer
    if result.overall_confidence < threshold:
        final_answer = "Information not found with sufficient confidence."
        
    return {
        "answer": final_answer,
        "confidence": result.overall_confidence,
        "chunks": chunks
    }

@app.tool(output="status")
def init_agent(ersatz_path: str, index_path: str) -> Dict[str, str]:
    global cognitron_agent
    try:
        CognitronAgent = load_ersatz_modules(ersatz_path)
        cognitron_agent = CognitronAgent(
            index_path=Path(index_path),
            memory_path=Path(index_path).parent / "memory.db",
            confidence_threshold=0.80
        )
        app.logger.info("Ersatz Agent initialized")
        return {"status": "initialized"}
    except Exception as e:
        app.logger.error(f"Initialization failed: {e}")
        return {"status": "failed", "error": str(e)}

if __name__ == "__main__":
    app.run(transport="stdio")