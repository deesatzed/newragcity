from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
import json
import time
import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("leann")

app = FastAPI()

# CORS for admin frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RequestMetrics:
    def __init__(self) -> None:
        self.request_count: int = 0
        self.total_processing_time: float = 0.0
        self.error_count: int = 0


metrics = RequestMetrics()

# In-memory storage for chunks (minimal functional store)
DOCUMENTS: List[Dict[str, Any]] = []


@app.middleware("http")
async def request_logger(request: Request, call_next):
    request_id = uuid.uuid4().hex[:8]
    start = time.perf_counter()
    path = request.url.path
    method = request.method
    logger.info(json.dumps({
        "event": "request_start",
        "request_id": request_id,
        "method": method,
        "path": path,
        "ts": datetime.utcnow().isoformat()
    }))
    status_code = 500
    try:
        response = await call_next(request)
        status_code = getattr(response, "status_code", 200)
        return response
    except Exception as e:
        metrics.error_count += 1
        logger.exception(f"[{request_id}] Error on {method} {path}: {e}")
        raise
    finally:
        dur = time.perf_counter() - start
        metrics.request_count += 1
        metrics.total_processing_time += dur
        logger.info(json.dumps({
            "event": "request_end",
            "request_id": request_id,
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(dur * 1000, 3),
            "ts": datetime.utcnow().isoformat()
        }))

@app.get("/health")
def health():
    logger.info("Health check called")
    return {"status": "healthy", "service": "leann"}


@app.get("/metrics")
def metrics_endpoint():
    avg_ms = (metrics.total_processing_time / metrics.request_count * 1000.0) if metrics.request_count else 0.0
    return {
        "service": "leann",
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": {
            "requests": metrics.request_count,
            "avg_response_ms": round(avg_ms, 3),
            "errors": metrics.error_count
        }
    }


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    limit: int = Field(10, ge=1, le=100, description="Max results")
    include_metadata: bool = Field(False, description="Include metadata in results")


@app.post("/search")
def search(req: SearchRequest):
    """
    Minimal search endpoint. Returns no results if no index is connected.
    This is a functional stub (not mocked data) to support integration.
    """
    q = (req.query or "").strip().lower()
    results: List[Dict[str, Any]] = []
    if q:
        tokens = [t for t in re.split(r"\W+", q) if t]
        for doc in DOCUMENTS:
            text = str(doc.get("text", ""))
            meta = doc.get("metadata", {}) or {}
            tl = text.lower()
            if not tl:
                continue
            matched = []
            first_idx = None
            for t in tokens:
                idx = tl.find(t)
                if idx != -1:
                    matched.append(t)
                    if first_idx is None or idx < first_idx:
                        first_idx = idx
            if matched:
                # score: fraction of tokens matched
                score = len(matched) / max(1, len(tokens))
                # snippet around first matched token
                if first_idx is None:
                    first_idx = 0
                start = max(0, first_idx - 80)
                end = min(len(text), first_idx + 120)
                snippet = text[start:end]
                results.append({
                    "title": meta.get("title") or meta.get("source_file") or "Document",
                    "snippet": snippet,
                    "score": round(float(score), 3),
                    "metadata": meta if req.include_metadata else None
                })
    # Truncate
    results.sort(key=lambda r: r.get("score", 0.0), reverse=True)
    results = results[: req.limit]
    return {"query": req.query, "results": results, "limit": req.limit}


class Chunk(BaseModel):
    text: str = Field(..., description="Chunk text content")
    metadata: Dict[str, Any] | None = Field(None, description="Optional metadata")


class UpsertRequest(BaseModel):
    chunks: List[Chunk] = Field(..., description="List of text chunks with optional metadata")


@app.post("/upsert")
def upsert(req: UpsertRequest):
    processed = 0
    for ch in req.chunks or []:
        DOCUMENTS.append({
            "text": ch.text,
            "metadata": ch.metadata or {}
        })
        processed += 1
    return {"processed": processed, "status": "ok", "total": len(DOCUMENTS)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
