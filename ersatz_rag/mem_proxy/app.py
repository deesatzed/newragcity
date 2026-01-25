from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
import json
import time
import uuid
from datetime import datetime
from pathlib import Path
import re

# Configure app
app = FastAPI(title="Mem Proxy", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics
class RequestMetrics:
    def __init__(self) -> None:
        self.request_count: int = 0
        self.total_processing_time: float = 0.0
        self.error_count: int = 0

metrics = RequestMetrics()

@app.middleware("http")
async def request_logger(request: Request, call_next):
    req_id = uuid.uuid4().hex[:8]
    start = time.perf_counter()
    path = request.url.path
    method = request.method
    try:
        response = await call_next(request)
        status_code = getattr(response, "status_code", 200)
        return response
    except Exception:
        metrics.error_count += 1
        raise
    finally:
        dur = time.perf_counter() - start
        metrics.request_count += 1
        metrics.total_processing_time += dur
        # Structured JSON line for observability
        print(json.dumps({
            "event": "request",
            "request_id": req_id,
            "method": method,
            "path": path,
            "status_code": locals().get("status_code", 500),
            "duration_ms": round(dur * 1000, 3),
            "ts": datetime.utcnow().isoformat()
        }))

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "mem-proxy"}

@app.get("/")
async def root():
    return {"message": "Mem Proxy running"}

@app.get("/metrics")
async def metrics_endpoint():
    avg_ms = (metrics.total_processing_time / metrics.request_count * 1000.0) if metrics.request_count else 0.0
    return {
        "service": "mem-proxy",
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": {
            "requests": metrics.request_count,
            "avg_response_ms": round(avg_ms, 3),
            "errors": metrics.error_count
        }
    }

# Models
class ClarifyRequest(BaseModel):
    query: str = Field(...)
    context: dict | None = Field(default=None)

class NoteRequest(BaseModel):
    title: str = Field(...)
    body_md: str = Field(..., description="Markdown body")
    tags: list[str] | None = Field(default=None)
    context: dict | None = Field(default=None)

# Utilities
MEM_DIR = Path(os.getenv("MEM_PROXY_MEMORY_DIR", "/app/memory")).resolve()
MEM_DIR.mkdir(parents=True, exist_ok=True)

SAFE_SLUG_RE = re.compile(r"[^a-zA-Z0-9_-]+")

def slugify(s: str) -> str:
    s = s.strip().replace(" ", "_")
    s = SAFE_SLUG_RE.sub("", s)
    return s[:80] or uuid.uuid4().hex[:8]

@app.post("/clarify")
async def clarify(req: ClarifyRequest):
    # Feature flag
    enabled = os.getenv("MEM_AGENT_ENABLED", "0").lower() in {"1", "true", "yes"}
    trace_id = uuid.uuid4().hex

    if not enabled:
        # Non-destructive passthrough with explicit mode
        return {
            "clarified_query": req.query,
            "filters": None,
            "rationale": None,
            "mode": "passthrough",
            "trace_id": trace_id
        }

    # If enabled, we expect an MCP connection to mem-agent (not wired yet)
    # Return 503 rather than fabricating results
    raise HTTPException(status_code=503, detail="mem-agent MCP not configured in mem-proxy")

@app.post("/note")
async def write_note(req: NoteRequest):
    # Writing notes does not require mem-agent if we treat the memory store as a sandboxed volume
    # This is a real side-effect with audit trail.
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    time_str = datetime.utcnow().strftime("%H%M%S")
    folder = MEM_DIR / date_str
    folder.mkdir(parents=True, exist_ok=True)

    filename = f"{time_str}_{slugify(req.title)}.md"
    path = folder / filename

    header = [
        f"# {req.title}",
        f"- created_utc: {datetime.utcnow().isoformat()}",
    ]
    if req.tags:
        header.append(f"- tags: {', '.join(req.tags)}")
    if req.context:
        try:
            header.append(f"- context: {json.dumps(req.context, separators=(',', ':'))}")
        except Exception:
            header.append(f"- context: <unserializable>")

    content = "\n".join(header) + "\n\n" + req.body_md.strip() + "\n"

    # Prevent directory traversal
    path = Path(str(path))
    if not str(path.resolve()).startswith(str(MEM_DIR)):
        raise HTTPException(status_code=400, detail="Invalid path")

    path.write_text(content, encoding="utf-8")

    return {
        "status": "ok",
        "path": str(path.relative_to(MEM_DIR)),
        "abs_path": str(path),
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)
