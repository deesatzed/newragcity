from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import logging
import time
import uuid
from datetime import datetime
import io
try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover
    PdfReader = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pageindex")

app = FastAPI()

# Allow cross-origin requests from admin frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RequestMetrics:
    """Simple in-memory metrics for requests"""
    def __init__(self) -> None:
        self.request_count: int = 0
        self.total_processing_time: float = 0.0
        self.error_count: int = 0


metrics = RequestMetrics()


@app.middleware("http")
async def request_logger(request: Request, call_next):
    request_id = uuid.uuid4().hex[:8]
    start_time = time.perf_counter()
    path = request.url.path
    method = request.method
    logger.info(json.dumps({
        "event": "request_start",
        "request_id": request_id,
        "method": method,
        "path": path,
        "timestamp": datetime.utcnow().isoformat()
    }))
    status_code = 500
    try:
        response = await call_next(request)
        status_code = getattr(response, "status_code", 200)
        return response
    except Exception as e:
        metrics.error_count += 1
        logger.exception(f"[{request_id}] Unhandled error on {method} {path}: {e}")
        raise
    finally:
        duration = time.perf_counter() - start_time
        metrics.request_count += 1
        metrics.total_processing_time += duration
        logger.info(json.dumps({
            "event": "request_end",
            "request_id": request_id,
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(duration * 1000, 3),
            "timestamp": datetime.utcnow().isoformat()
        }))

@app.get("/health")
async def health():
    logger.info("Health check called")
    return {"status": "healthy", "service": "pageindex"}

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Welcome to PageIndex Service"}

@app.post("/extract_structure")
async def extract_structure(file: UploadFile = File(...)):
    try:
        content = await file.read()
        size = len(content)
        text_content = ""
        pages = None
        # If PDF, try extracting real text
        is_pdf = (file.filename or "").lower().endswith(".pdf") or (file.content_type == "application/pdf")
        if is_pdf and PdfReader is not None:
            try:
                reader = PdfReader(io.BytesIO(content))
                pages = len(reader.pages)
                texts = []
                for p in reader.pages:
                    try:
                        t = p.extract_text() or ""
                    except Exception:
                        t = ""
                    if t:
                        texts.append(t)
                text_content = "\n".join(texts)
            except Exception as pe:
                logger.warning(f"PDF extraction failed, falling back to binary decode: {pe}")
        # Fallback to best-effort decode if no text extracted
        if not text_content:
            text_content = content[:20000].decode("utf-8", errors="ignore")
        word_count = len(text_content.split())
        line_count = text_content.count("\n") + 1 if text_content else 0
        logger.info(json.dumps({
            "event": "extract_structure",
            "filename": file.filename,
            "size": size,
            "content_type": file.content_type,
            "word_count": word_count
        }))
        return {
            "structure": {
                "file_name": file.filename,
                "content_type": file.content_type,
                "size_bytes": size,
                "pages": pages,
                "summary": {
                    "word_count": word_count,
                    "line_count": line_count
                },
                "preview": text_content[:500]
            },
            "text": text_content,
            "status": "success"
        }
    except Exception as e:
        logger.exception(f"Failed to extract structure: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
def metrics_endpoint():
    avg_ms = (metrics.total_processing_time / metrics.request_count * 1000.0) if metrics.request_count else 0.0
    return {
        "service": "pageindex",
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": {
            "requests": metrics.request_count,
            "avg_response_ms": round(avg_ms, 3),
            "errors": metrics.error_count
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
