from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
import json
import time
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("deepconf")

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
async def health():
    logger.info("Health check called")
    return {"status": "healthy", "service": "deepConf"}

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Welcome to deepConf Service"}

@app.post("/validate_confidence")
async def validate_confidence(request: Request):
    body = await request.json()
    logger.info(f"Validate confidence called")
    
    # In a real implementation, this would analyze the confidence
    # based on multiple signals
    confidence_score = 0.87
    
    return {
        "confidence": confidence_score,
        "threshold": 0.75,
        "pass": confidence_score >= 0.75,
        "status": "success"
    }


@app.get("/metrics")
def metrics_endpoint():
    avg_ms = (metrics.total_processing_time / metrics.request_count * 1000.0) if metrics.request_count else 0.0
    return {
        "service": "deepconf",
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": {
            "requests": metrics.request_count,
            "avg_response_ms": round(avg_ms, 3),
            "errors": metrics.error_count
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
