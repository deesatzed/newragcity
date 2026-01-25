"""
WebSocket Handler for Real-Time Collective Reasoning

This implements WebSocket support from Phase 1 Week 1-2:
- Bi-directional real-time communication for Deep Chat
- Connection management and authentication
- Message protocol for interactive reasoning sessions
- Error handling and connection recovery
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
import uuid

from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.routing import APIRouter
from pydantic import BaseModel, ValidationError

from app.three_approach_integration import ThreeApproachRAG
from app.config import get_index_path

logger = logging.getLogger(__name__)

# WebSocket Message Models
class WebSocketMessage(BaseModel):
    """Base WebSocket message format"""
    type: str
    session_id: str
    timestamp: str
    data: Dict[str, Any] = {}

class ReasoningRequest(BaseModel):
    """Request to start reasoning session"""
    query: str
    top_k: int = 10
    confidence_threshold: float = 0.8
    enable_citations: bool = True
    streaming_speed: str = "normal"  # "fast", "normal", "slow"

class ReasoningResponse(BaseModel):
    """Response with reasoning results"""
    results: List[Dict[str, Any]]
    confidence_analysis: Dict[str, Any]
    approach_summary: Dict[str, Any]
    citations: List[Dict[str, Any]] = []

class ConnectionManager:
    """Manage WebSocket connections for collective reasoning"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        self.session_data: Dict[str, Dict[str, Any]] = {}
        self.reasoning_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str, client_info: Dict[str, Any]):
        """Accept and register new WebSocket connection"""
        
        await websocket.accept()
        
        self.active_connections[session_id] = websocket
        self.connection_metadata[session_id] = {
            "client_info": client_info,
            "connected_at": datetime.now().isoformat(),
            "status": "connected",
            "messages_sent": 0,
            "messages_received": 0
        }
        
        logger.info(f"🔌 WebSocket connected: {session_id}")
        
        # Send welcome message
        welcome_msg = WebSocketMessage(
            type="connection_established",
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            data={
                "message": "Connected to Collective Intelligence System",
                "capabilities": [
                    "real_time_reasoning",
                    "streaming_confidence_updates",
                    "interactive_citations",
                    "transparent_ai_decision_making"
                ],
                "version": "1.0.0-phase1"
            }
        )
        
        await self.send_message(session_id, welcome_msg.dict())
    
    def disconnect(self, session_id: str):
        """Disconnect and cleanup WebSocket connection"""
        
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        
        if session_id in self.connection_metadata:
            self.connection_metadata[session_id]["status"] = "disconnected"
            self.connection_metadata[session_id]["disconnected_at"] = datetime.now().isoformat()
        
        logger.info(f"🔌 WebSocket disconnected: {session_id}")
    
    async def send_message(self, session_id: str, message: Dict[str, Any]):
        """Send message to specific WebSocket connection"""
        
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            try:
                await websocket.send_text(json.dumps(message))
                
                # Update message count
                if session_id in self.connection_metadata:
                    self.connection_metadata[session_id]["messages_sent"] += 1
                
            except Exception as e:
                logger.error(f"Failed to send message to {session_id}: {e}")
                self.disconnect(session_id)
    
    async def broadcast_message(self, message: Dict[str, Any], exclude_sessions: Optional[Set[str]] = None):
        """Broadcast message to all connected clients"""
        
        if exclude_sessions is None:
            exclude_sessions = set()
        
        disconnect_sessions = []
        
        for session_id, websocket in self.active_connections.items():
            if session_id not in exclude_sessions:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Failed to broadcast to {session_id}: {e}")
                    disconnect_sessions.append(session_id)
        
        # Clean up failed connections
        for session_id in disconnect_sessions:
            self.disconnect(session_id)
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific session"""
        return self.connection_metadata.get(session_id)
    
    def list_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return list(self.active_connections.keys())

# Global connection manager
connection_manager = ConnectionManager()

# WebSocket router
websocket_router = APIRouter(prefix="/api/ws", tags=["websocket"])

@websocket_router.websocket("/collective-reasoning/{session_id}")
async def websocket_collective_reasoning(
    websocket: WebSocket,
    session_id: str,
    rag: ThreeApproachRAG = Depends(lambda: ThreeApproachRAG(enable_streaming=True)),
    index_path: str = Depends(get_index_path)
):
    """
    WebSocket endpoint for real-time collective reasoning
    
    Provides bi-directional communication for interactive AI reasoning sessions.
    """
    
    client_info = {
        "client_host": websocket.client.host,
        "user_agent": websocket.headers.get("user-agent", "unknown")
    }
    
    await connection_manager.connect(websocket, session_id, client_info)
    
    try:
        while True:
            # Receive message from client
            message_text = await websocket.receive_text()
            
            try:
                message_data = json.loads(message_text)
                await handle_websocket_message(session_id, message_data, rag, index_path)
                
                # Update received message count
                if session_id in connection_manager.connection_metadata:
                    connection_manager.connection_metadata[session_id]["messages_received"] += 1
                
            except json.JSONDecodeError:
                error_response = {
                    "type": "error",
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                    "data": {
                        "error": "Invalid JSON format",
                        "message": "Please send valid JSON messages"
                    }
                }
                await connection_manager.send_message(session_id, error_response)
            
            except ValidationError as e:
                error_response = {
                    "type": "validation_error",
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                    "data": {
                        "error": "Message validation failed",
                        "details": str(e)
                    }
                }
                await connection_manager.send_message(session_id, error_response)
            
    except WebSocketDisconnect:
        connection_manager.disconnect(session_id)
        logger.info(f"🔌 WebSocket client {session_id} disconnected")
    
    except Exception as e:
        logger.error(f"WebSocket error for {session_id}: {e}")
        
        error_response = {
            "type": "server_error", 
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "error": str(e),
                "error_type": type(e).__name__
            }
        }
        
        try:
            await connection_manager.send_message(session_id, error_response)
        except:
            pass  # Connection might already be closed
        
        connection_manager.disconnect(session_id)

async def handle_websocket_message(
    session_id: str,
    message_data: Dict[str, Any],
    rag: ThreeApproachRAG,
    index_path: str
):
    """Handle incoming WebSocket messages"""
    
    message_type = message_data.get("type")
    
    if message_type == "start_reasoning":
        await handle_start_reasoning(session_id, message_data, rag, index_path)
    
    elif message_type == "pause_reasoning":
        await handle_pause_reasoning(session_id, message_data)
    
    elif message_type == "resume_reasoning":
        await handle_resume_reasoning(session_id, message_data, rag, index_path)
    
    elif message_type == "stop_reasoning":
        await handle_stop_reasoning(session_id, message_data)
    
    elif message_type == "request_details":
        await handle_request_details(session_id, message_data)
    
    elif message_type == "ping":
        await handle_ping(session_id)
    
    else:
        # Unknown message type
        response = {
            "type": "unknown_message_type",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "received_type": message_type,
                "supported_types": [
                    "start_reasoning", "pause_reasoning", "resume_reasoning",
                    "stop_reasoning", "request_details", "ping"
                ]
            }
        }
        await connection_manager.send_message(session_id, response)

async def handle_start_reasoning(
    session_id: str,
    message_data: Dict[str, Any],
    rag: ThreeApproachRAG,
    index_path: str
):
    """Handle start reasoning request"""
    
    try:
        request_data = message_data.get("data", {})
        reasoning_request = ReasoningRequest(**request_data)
        
        # Store reasoning session info
        connection_manager.reasoning_sessions[session_id] = {
            "status": "active",
            "query": reasoning_request.query,
            "started_at": datetime.now().isoformat(),
            "streaming_speed": reasoning_request.streaming_speed
        }
        
        # Send acknowledgment
        ack_response = {
            "type": "reasoning_started",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "query": reasoning_request.query,
                "session_status": "active"
            }
        }
        await connection_manager.send_message(session_id, ack_response)
        
        # Start streaming reasoning updates
        await stream_reasoning_updates(session_id, reasoning_request, rag, index_path)
        
    except Exception as e:
        error_response = {
            "type": "reasoning_start_error",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "error": str(e),
                "query": message_data.get("data", {}).get("query", "unknown")
            }
        }
        await connection_manager.send_message(session_id, error_response)

async def stream_reasoning_updates(
    session_id: str,
    request: ReasoningRequest,
    rag: ThreeApproachRAG,
    index_path: str
):
    """Stream reasoning updates to WebSocket client"""
    
    try:
        # Determine streaming delay based on speed preference
        speed_delays = {
            "fast": 0.01,
            "normal": 0.05,
            "slow": 0.1
        }
        delay = speed_delays.get(request.streaming_speed, 0.05)
        
        # Stream reasoning updates
        async for update in rag.streaming_collective_reasoning(
            query=request.query,
            index_path=index_path,
            top_k=request.top_k
        ):
            # Check if session is still active
            session_info = connection_manager.reasoning_sessions.get(session_id)
            if not session_info or session_info.get("status") != "active":
                break
            
            # Format update for WebSocket
            ws_update = {
                "type": "reasoning_update",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "data": update
            }
            
            await connection_manager.send_message(session_id, ws_update)
            
            # Add speed-based delay
            await asyncio.sleep(delay)
        
        # Mark session as completed
        if session_id in connection_manager.reasoning_sessions:
            connection_manager.reasoning_sessions[session_id]["status"] = "completed"
            connection_manager.reasoning_sessions[session_id]["completed_at"] = datetime.now().isoformat()
        
    except Exception as e:
        logger.error(f"Streaming error for session {session_id}: {e}")
        
        error_response = {
            "type": "reasoning_stream_error",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "error": str(e),
                "error_type": type(e).__name__
            }
        }
        
        await connection_manager.send_message(session_id, error_response)

async def handle_pause_reasoning(session_id: str, message_data: Dict[str, Any]):
    """Handle pause reasoning request"""
    
    if session_id in connection_manager.reasoning_sessions:
        connection_manager.reasoning_sessions[session_id]["status"] = "paused"
        connection_manager.reasoning_sessions[session_id]["paused_at"] = datetime.now().isoformat()
    
    response = {
        "type": "reasoning_paused",
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "data": {"message": "Reasoning session paused"}
    }
    
    await connection_manager.send_message(session_id, response)

async def handle_resume_reasoning(
    session_id: str,
    message_data: Dict[str, Any],
    rag: ThreeApproachRAG,
    index_path: str
):
    """Handle resume reasoning request"""
    
    if session_id in connection_manager.reasoning_sessions:
        session_info = connection_manager.reasoning_sessions[session_id]
        
        if session_info.get("status") == "paused":
            session_info["status"] = "active"
            session_info["resumed_at"] = datetime.now().isoformat()
            
            response = {
                "type": "reasoning_resumed",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "data": {"message": "Reasoning session resumed"}
            }
            
            await connection_manager.send_message(session_id, response)
        else:
            response = {
                "type": "reasoning_resume_error",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "data": {"error": "Session is not in paused state"}
            }
            
            await connection_manager.send_message(session_id, response)

async def handle_stop_reasoning(session_id: str, message_data: Dict[str, Any]):
    """Handle stop reasoning request"""
    
    if session_id in connection_manager.reasoning_sessions:
        connection_manager.reasoning_sessions[session_id]["status"] = "stopped"
        connection_manager.reasoning_sessions[session_id]["stopped_at"] = datetime.now().isoformat()
    
    response = {
        "type": "reasoning_stopped",
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "data": {"message": "Reasoning session stopped"}
    }
    
    await connection_manager.send_message(session_id, response)

async def handle_request_details(session_id: str, message_data: Dict[str, Any]):
    """Handle request for session details"""
    
    session_info = connection_manager.get_session_info(session_id)
    reasoning_info = connection_manager.reasoning_sessions.get(session_id, {})
    
    response = {
        "type": "session_details",
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "data": {
            "connection_info": session_info,
            "reasoning_session": reasoning_info,
            "active_connections": connection_manager.get_connection_count()
        }
    }
    
    await connection_manager.send_message(session_id, response)

async def handle_ping(session_id: str):
    """Handle ping message (for connection keepalive)"""
    
    response = {
        "type": "pong",
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "data": {
            "message": "Connection alive",
            "server_time": datetime.now().isoformat()
        }
    }
    
    await connection_manager.send_message(session_id, response)

# Additional WebSocket endpoints

@websocket_router.websocket("/system-monitor/{session_id}")
async def websocket_system_monitor(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for system monitoring and statistics"""
    
    await websocket.accept()
    
    try:
        while True:
            # Send system statistics every 5 seconds
            stats = {
                "type": "system_stats",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "active_connections": connection_manager.get_connection_count(),
                    "active_reasoning_sessions": len([
                        s for s in connection_manager.reasoning_sessions.values() 
                        if s.get("status") == "active"
                    ]),
                    "total_sessions": len(connection_manager.reasoning_sessions),
                    "system_load": "normal"  # Would be actual system metrics
                }
            }
            
            await websocket.send_text(json.dumps(stats))
            await asyncio.sleep(5)
    
    except WebSocketDisconnect:
        logger.info(f"System monitor {session_id} disconnected")

# Utility functions for WebSocket management

def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance"""
    return connection_manager

def generate_session_id() -> str:
    """Generate a unique session ID"""
    return f"ws_{uuid.uuid4().hex[:12]}"