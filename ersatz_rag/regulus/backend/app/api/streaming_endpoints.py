"""
Streaming API Endpoints for Real-Time Collective Reasoning

This implements the streaming API endpoints from Phase 1 Week 1-2:
- Server-Sent Events (SSE) for real-time reasoning updates
- FastAPI streaming endpoints for Deep Chat integration
- Message protocol for collective intelligence transparency
- Error handling and connection management for streaming
"""

import asyncio
import json
import logging
from typing import AsyncGenerator, Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from starlette.requests import Request
from starlette.responses import Response
from pydantic import BaseModel, Field

from app.three_approach_integration import ThreeApproachRAG
from app.config import get_index_path

logger = logging.getLogger(__name__)

# Request/Response Models
class CollectiveReasoningRequest(BaseModel):
    """Request model for collective reasoning"""
    query: str = Field(..., description="Query to process", min_length=1)
    top_k: int = Field(default=10, description="Number of results to return", ge=1, le=50)
    enable_streaming: bool = Field(default=True, description="Enable real-time streaming")
    session_id: Optional[str] = Field(None, description="Optional session ID for tracking")
    include_citations: bool = Field(default=True, description="Include citation information")
    confidence_threshold: float = Field(default=0.8, description="Confidence threshold", ge=0.0, le=1.0)

class StreamingMessage(BaseModel):
    """Streaming message format"""
    session_id: str
    step: str
    status: str  # "processing", "completed", "error"
    message: str
    timestamp: str
    progress: float = Field(ge=0.0, le=1.0)
    data: Optional[Dict[str, Any]] = None

# Router for streaming endpoints
streaming_router = APIRouter(prefix="/api/streaming", tags=["streaming"])

# Global RAG system instance (would be dependency injected in production)
rag_system = None

def get_rag_system() -> ThreeApproachRAG:
    """Dependency to get RAG system instance"""
    global rag_system
    if rag_system is None:
        rag_system = ThreeApproachRAG(
            embedding_model="ibm-granite/granite-embedding-english-r2",
            confidence_threshold=0.80,
            enable_streaming=True
        )
    return rag_system

@streaming_router.post("/collective-reasoning")
async def collective_reasoning_stream(
    request: CollectiveReasoningRequest,
    rag: ThreeApproachRAG = Depends(get_rag_system),
    index_path: str = Depends(get_index_path)
):
    """
    Stream collective reasoning process with real-time updates
    
    This endpoint provides real-time streaming of the collective intelligence
    reasoning process for transparent AI decision-making.
    """
    
    logger.info(f"🚀 Starting collective reasoning stream for: '{request.query}'")
    
    async def generate_stream():
        try:
            # Generate session ID if not provided
            session_id = request.session_id or f"reasoning_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Stream the reasoning process
            async for update in rag.streaming_collective_reasoning(
                query=request.query,
                index_path=index_path,
                top_k=request.top_k
            ):
                # Format as Server-Sent Event
                message = StreamingMessage(
                    session_id=update.get("session_id", session_id),
                    step=update.get("step", "unknown"),
                    status=update.get("status", "processing"),
                    message=update.get("message", ""),
                    timestamp=update.get("timestamp", datetime.now().isoformat()),
                    progress=update.get("progress", 0.0),
                    data=update.get("data")
                )
                
                # Convert to SSE format
                sse_data = f"data: {message.json()}\n\n"
                yield sse_data.encode()
                
                # Small delay to prevent overwhelming client
                await asyncio.sleep(0.01)
            
            # Send completion event
            completion_message = StreamingMessage(
                session_id=session_id,
                step="stream_complete",
                status="completed",
                message="Collective reasoning stream completed",
                timestamp=datetime.now().isoformat(),
                progress=1.0
            )
            
            yield f"data: {completion_message.json()}\n\n".encode()
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            
            error_message = StreamingMessage(
                session_id=session_id,
                step="error",
                status="error",
                message=f"Streaming error: {str(e)}",
                timestamp=datetime.now().isoformat(),
                progress=0.0,
                data={"error_type": type(e).__name__}
            )
            
            yield f"data: {error_message.json()}\n\n".encode()
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )

@streaming_router.get("/collective-reasoning-sse")
async def collective_reasoning_sse(
    query: str = Query(..., description="Query to process"),
    top_k: int = Query(default=10, description="Number of results", ge=1, le=50),
    confidence_threshold: float = Query(default=0.8, ge=0.0, le=1.0),
    rag: ThreeApproachRAG = Depends(get_rag_system),
    index_path: str = Depends(get_index_path)
):
    """
    Server-Sent Events endpoint for collective reasoning
    
    Alternative endpoint using query parameters for simpler client integration.
    """
    
    logger.info(f"📡 SSE collective reasoning for: '{query}'")
    
    async def sse_stream():
        try:
            session_id = f"sse_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Set SSE headers
            yield "retry: 10000\n"
            yield f"id: {session_id}\n"
            yield "event: start\n"
            yield f"data: {{\"message\": \"Starting collective reasoning for: {query}\"}}\n\n"
            
            # Stream reasoning updates
            async for update in rag.streaming_collective_reasoning(query, index_path, top_k):
                event_type = update.get("step", "update")
                update_json = json.dumps(update)
                
                yield f"event: {event_type}\n"
                yield f"data: {update_json}\n\n"
                
                await asyncio.sleep(0.01)
            
            # Final completion event
            yield "event: complete\n"
            yield f"data: {{\"message\": \"Collective reasoning completed\", \"session_id\": \"{session_id}\"}}\n\n"
            
        except Exception as e:
            logger.error(f"SSE streaming error: {e}")
            yield "event: error\n"
            yield f"data: {{\"error\": \"{str(e)}\", \"type\": \"{type(e).__name__}\"}}\n\n"
    
    return StreamingResponse(
        sse_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
            "X-Accel-Buffering": "no"
        }
    )

@streaming_router.post("/enhanced-search")
async def enhanced_search_stream(
    request: CollectiveReasoningRequest,
    background_tasks: BackgroundTasks,
    rag: ThreeApproachRAG = Depends(get_rag_system),
    index_path: str = Depends(get_index_path)
):
    """
    Enhanced search with optional streaming
    
    Supports both streaming and non-streaming modes based on request.
    """
    
    logger.info(f"🔍 Enhanced search request: '{request.query}' (streaming: {request.enable_streaming})")
    
    if request.enable_streaming:
        # Return streaming response
        return await collective_reasoning_stream(request, rag, index_path)
    else:
        # Return non-streaming response
        try:
            result = rag.enhanced_hybrid_search(
                query=request.query,
                index_path=index_path,
                top_k=request.top_k
            )
            
            # Log usage for analytics
            background_tasks.add_task(log_search_usage, request.query, len(result.get("results", [])))
            
            return {
                "status": "completed",
                "query": request.query,
                "session_id": request.session_id,
                "timestamp": datetime.now().isoformat(),
                "streaming_enabled": False,
                **result
            }
            
        except Exception as e:
            logger.error(f"Enhanced search error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

@streaming_router.get("/system-status")
async def get_system_status(rag: ThreeApproachRAG = Depends(get_rag_system)):
    """Get streaming system status and capabilities"""
    
    system_status = rag.get_system_status()
    
    streaming_capabilities = {
        "streaming_enabled": rag.enable_streaming,
        "supported_endpoints": [
            "/collective-reasoning",
            "/collective-reasoning-sse", 
            "/enhanced-search"
        ],
        "supported_events": [
            "query_processing",
            "query_analysis",
            "search_initialization",
            "semantic_search",
            "confidence_calibration",
            "final_results"
        ],
        "message_protocol": "streaming_message_v1",
        "max_concurrent_streams": 100,  # Would be configurable
        "stream_timeout_seconds": 300
    }
    
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "system_info": system_status,
        "streaming_capabilities": streaming_capabilities,
        "performance_targets": {
            "search_accuracy_improvement": "25% (hybrid search)",
            "confidence_calibration_improvement": "30% overconfidence reduction",
            "citation_accuracy_target": "95%",
            "streaming_latency_target": "<500ms per update"
        }
    }

@streaming_router.get("/health")
async def health_check():
    """Health check endpoint for streaming services"""
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "collective_reasoning_streaming",
        "version": "1.0.0-phase1-week1-2"
    }

# Utility Functions

async def log_search_usage(query: str, result_count: int):
    """Log search usage for analytics (background task)"""
    
    try:
        # In production, this would write to a proper analytics system
        usage_log = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "result_count": result_count,
            "query_length": len(query.split()),
            "service": "enhanced_search"
        }
        
        logger.info(f"📊 Search usage logged: {usage_log}")
        
    except Exception as e:
        logger.error(f"Failed to log search usage: {e}")

def format_streaming_error(error: Exception, session_id: str) -> dict:
    """Format streaming error for client consumption"""
    
    return {
        "session_id": session_id,
        "step": "error",
        "status": "error",
        "message": f"Streaming error: {str(error)}",
        "timestamp": datetime.now().isoformat(),
        "progress": 0.0,
        "data": {
            "error_type": type(error).__name__,
            "error_details": str(error),
            "recovery_suggestions": [
                "Check network connection",
                "Retry with simpler query",
                "Contact support if issue persists"
            ]
        }
    }

# Connection Management

class ConnectionManager:
    """Manage streaming connections and sessions"""
    
    def __init__(self):
        self.active_connections: Dict[str, Any] = {}
        self.session_stats: Dict[str, Dict[str, Any]] = {}
    
    def add_connection(self, session_id: str, connection_info: Dict[str, Any]):
        """Add a new streaming connection"""
        self.active_connections[session_id] = connection_info
        self.session_stats[session_id] = {
            "start_time": datetime.now().isoformat(),
            "messages_sent": 0,
            "status": "active"
        }
    
    def remove_connection(self, session_id: str):
        """Remove a streaming connection"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        
        if session_id in self.session_stats:
            self.session_stats[session_id]["status"] = "completed"
            self.session_stats[session_id]["end_time"] = datetime.now().isoformat()
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            "active_connections": len(self.active_connections),
            "total_sessions": len(self.session_stats),
            "session_details": dict(list(self.session_stats.items())[-10:])  # Last 10 sessions
        }

# Global connection manager
connection_manager = ConnectionManager()

@streaming_router.get("/connections")
async def get_connection_stats():
    """Get streaming connection statistics"""
    return connection_manager.get_connection_stats()