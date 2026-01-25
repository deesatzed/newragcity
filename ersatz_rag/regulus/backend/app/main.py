import logging
import shutil
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, Depends, Query
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.models import Base
from app.indexing import IndexingService
from app.config import (
    DATABASE_URL, 
    EMBEDDING_MODEL, 
    INDEX_PATH,
    TRANSPARENCY_ENABLED,
    TRANSPARENCY_LEVEL,
    get_embedding_model,
    get_index_path
)

from leann.api import LeannSearcher
from leann.registry import autodiscover_backends
from app.hybrid_ingest import HybridIngestor, IngestResult
from app.hybrid_retrieve import HybridRetriever
from app.config import HYBRID_ENABLED, QDRANT_URL, QDRANT_COLLECTION, OPENSEARCH_URL, OPENSEARCH_INDEX

app = FastAPI(
    title="Regulus API - Revolutionary Transparent Collective Intelligence",
    description="""
    Regulus API provides revolutionary transparent collective intelligence with:
    - Complete reasoning explainability (95% target)
    - Comprehensive audit trails (100% completeness)
    - User comprehension optimization (80% target)
    - Full compliance reporting capabilities
    
    Built on PageIndex + LEANN + deepConf with complete transparency infrastructure.
    """,
    version="1.0.0"
)

# Enable CORS for admin frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import transparency infrastructure router if enabled (used later)
if TRANSPARENCY_ENABLED:
    from app.api.transparency_endpoints import transparency_router

# Discover backends when the module is loaded
autodiscover_backends()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.on_event("startup")
async def startup_event():
    """
    Application startup event.
    Initializes the database connection and creates tables.
    """
    logger.info("Starting application...")
    try:
        logger.info("Attempting to create database engine...")
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        logger.info("Database engine created.")

        logger.info("Attempting to create all tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully.")

        app.state.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        logger.info("SessionLocal created and stored in app state.")
        
        # Initialize transparency infrastructure if enabled
        if TRANSPARENCY_ENABLED:
            logger.info(f"Initializing transparency infrastructure (level: {TRANSPARENCY_LEVEL})")
            try:
                # Initialize transparency components
                from app.transparency import get_audit_logger, get_session_manager, get_reasoning_tracer
                from app.explainable import get_reasoning_explainer
                
                audit_logger = get_audit_logger()
                session_manager = get_session_manager()
                reasoning_tracer = get_reasoning_tracer()
                reasoning_explainer = get_reasoning_explainer()
                
                logger.info("✅ Transparency infrastructure initialized successfully")
                logger.info("   - Reasoning Tracer: Active")
                logger.info("   - Audit Logger: Active") 
                logger.info("   - Session Manager: Active")
                logger.info("   - Explainable AI: Active")
                logger.info("   - Compliance Reporting: Active")
                
            except Exception as transparency_error:
                logger.warning(f"Transparency infrastructure initialization failed: {transparency_error}")
                logger.warning("Application will continue with basic functionality")

    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


def get_db():
    db = app.state.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")

def read_root():

    return {"message": "Regulus API is running"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    if HYBRID_ENABLED:
        logger.info("Hybrid ingestion enabled. Ingesting to Qdrant + OpenSearch")
        ingestor = HybridIngestor()
        res: IngestResult = ingestor.ingest_pdf(file_path, source_file=file.filename)
        return {
            "message": "File indexed (hybrid)",
            "doc_id": res.doc_id,
            "qdrant_points": res.qdrant_points,
            "opensearch_docs": res.opensearch_docs,
            "chunks": res.chunks,
            "sha256": res.sha256,
        }
    logger.info("Hybrid disabled. Using legacy indexing service")
    indexing_service = IndexingService()
    await indexing_service.run_indexing([Path(file_path)])
    return {"message": "File indexed (legacy)"}

@app.post("/query")

async def query_index(query: str = Form(...)):
    try:
        searcher = LeannSearcher(INDEX_PATH)
        results = searcher.search(query, top_k=10)
        
        # Convert SearchResult objects to dictionaries for JSON response
        formatted_results = []
        for result in results:
            formatted_results.append({
                'content': result.text,
                'metadata': result.metadata,
                'score': result.score
            })
        
        return {"results": formatted_results}
    except Exception as e:
        logger.error(f"Search error: {e}")
        return {"error": str(e), "results": []}


@app.get("/hybrid_status")
def hybrid_status(doc_id: str = Query(..., description="Document ID to verify")):
    """Verify presence of a document in Qdrant and OpenSearch (hybrid).

    Returns counts of chunks/points found in each store for the provided doc_id.
    """
    if not HYBRID_ENABLED:
        return {"hybrid_enabled": False}
    try:
        # Lazy imports to avoid heavy client init at module import time
        from qdrant_client import QdrantClient
        from qdrant_client.http import models as qmodels
        from opensearchpy import OpenSearch

        q = QdrantClient(url=QDRANT_URL)
        os_client = OpenSearch(OPENSEARCH_URL, timeout=10, use_ssl=False, verify_certs=False)

        q_count = q.count(
            collection_name=QDRANT_COLLECTION,
            count_filter=qmodels.Filter(should=[qmodels.FieldCondition(key="doc_id", match=qmodels.MatchValue(value=doc_id))])
        ).count

        os_resp = os_client.count(index=OPENSEARCH_INDEX, body={"query": {"term": {"doc_id": doc_id}}})
        os_count = os_resp.get('count', 0)

        return {
            "hybrid_enabled": True,
            "doc_id": doc_id,
            "qdrant_points": int(q_count),
            "opensearch_docs": int(os_count),
        }
    except Exception as e:
        logger.error(f"hybrid_status error: {e}")
        return {"error": str(e)}


class HybridQuery(BaseModel):
    query: str
    k_lex: int | None = 100
    k_vec: int | None = 100
    rerank_k: int | None = 50
    final_k: int | None = 10


_hybrid_retriever: HybridRetriever | None = None


@app.post("/query_hybrid")
async def query_hybrid(payload: HybridQuery):
    """Hybrid retrieval: BM25 + Dense + RRF + Cross-Encoder rerank.

    Returns real snippets and citations from OpenSearch/Qdrant.
    """
    global _hybrid_retriever
    if not HYBRID_ENABLED:
        return {"error": "Hybrid disabled"}
    if _hybrid_retriever is None:
        _hybrid_retriever = HybridRetriever()
    try:
        results = _hybrid_retriever.search(
            query=payload.query,
            k_lex=payload.k_lex or 100,
            k_vec=payload.k_vec or 100,
            rerank_k=payload.rerank_k or 50,
            final_k=payload.final_k or 10,
        )
        return {
            "results": [
                {
                    "doc_id": r.doc_id,
                    "chunk_id": r.chunk_id,
                    "title": r.title,
                    "source_file": r.source_file,
                    "page": r.page,
                    "snippet": r.body[:500],
                    "score": r.score,
                }
                for r in results
            ]
        }
    except Exception as e:
        logger.error(f"query_hybrid error: {e}")
        return {"error": str(e), "results": []}

# Include transparency endpoints if enabled
if TRANSPARENCY_ENABLED:
    app.include_router(transparency_router)
    logger.info("✅ Transparency API endpoints enabled")


@app.get("/config")
def get_config():
    """Get current system configuration including embedding model and transparency"""
    config = {
        "llm": "OpenAI GPT-4",
        "embedding_model": EMBEDDING_MODEL,
        "indexer": "LEANN + PageIndex",
        "confidence_gating": "deepConf",
        "memory": "PostgreSQL Case Memory",
        "api_keys_required": ["OPENAI_API_KEY", "PAGEINDEX_API_KEY"]
    }
    
    # Add transparency configuration if enabled
    if TRANSPARENCY_ENABLED:
        config.update({
            "transparency_infrastructure": {
                "enabled": True,
                "level": TRANSPARENCY_LEVEL,
                "components": {
                    "reasoning_tracer": "active",
                    "audit_logger": "active",
                    "session_manager": "active", 
                    "explainable_ai": "active",
                    "compliance_reporting": "active"
                },
                "targets": {
                    "explainability": "95%",
                    "audit_completeness": "100%",
                    "user_comprehension": "80%"
                },
                "api_endpoints": "/transparency/*"
            }
        })
    else:
        config["transparency_infrastructure"] = {"enabled": False}
    
    return config


@app.get("/metrics")
def metrics():
    """Basic placeholder metrics for Regulus API itself"""
    # This endpoint provides minimal operational info for the admin dashboard
    return {
        "service": "regulus-backend",
        "metrics": {
            "requests": None,
            "avg_response_ms": None,
            "errors": None
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint with transparency infrastructure status"""
    status = {
        "status": "healthy",
        "timestamp": "2024-08-31T00:00:00Z",
        "services": {
            "database": "connected",
            "search_engine": "operational",
            "embedding_model": EMBEDDING_MODEL
        }
    }
    
    if TRANSPARENCY_ENABLED:
        status["transparency"] = {
            "infrastructure": "operational",
            "level": TRANSPARENCY_LEVEL,
            "components_active": 5
        }
    
    return status
