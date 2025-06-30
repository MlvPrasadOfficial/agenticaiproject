"""
Agent Execution API endpoints for Enterprise Insights Copilot
Implements Tasks 50-54: Agent execution, workflows, sessions, conversations, real-time updates
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
import json
import asyncio
import logging
from dataclasses import asdict

from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.agent_manager import agent_manager
from app.services.session_manager import session_manager
from app.services.conversation_manager import conversation_manager

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api/v1/agents", tags=["Agent System"])

# Pydantic Models
class AgentExecutionRequest(BaseModel):
    agent_type: str = Field(..., description="Type of agent to execute (planning, data_analysis, query, insight)")
    query: str = Field(..., description="User query or task to execute")
    data_source: Optional[str] = Field(None, description="Data source file ID or reference")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional execution parameters")

class AgentExecutionResponse(BaseModel):
    execution_id: str
    agent_type: str
    status: str = Field(description="pending, running, completed, failed")
    session_id: str
    timestamp: datetime
    estimated_duration: Optional[int] = Field(None, description="Estimated completion time in seconds")

class WorkflowExecutionRequest(BaseModel):
    workflow_type: str = Field(..., description="Type of workflow (data_analysis, insight_generation, custom)")
    steps: List[Dict[str, Any]] = Field(..., description="Workflow steps configuration")
    data_source: Optional[str] = Field(None, description="Primary data source")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")

class WorkflowExecutionResponse(BaseModel):
    workflow_id: str
    workflow_type: str
    status: str
    session_id: str
    steps_total: int
    steps_completed: int
    timestamp: datetime

class SessionCreateRequest(BaseModel):
    user_id: Optional[str] = Field(None, description="User identifier")
    session_name: Optional[str] = Field(None, description="Optional session name")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Session metadata")

class SessionResponse(BaseModel):
    session_id: str
    user_id: Optional[str]
    session_name: Optional[str]
    created_at: datetime
    last_activity: datetime
    status: str
    conversation_count: int
    metadata: Dict[str, Any]

class ConversationMessage(BaseModel):
    role: str = Field(..., description="user, assistant, system")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ConversationRequest(BaseModel):
    session_id: str
    message: ConversationMessage
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ConversationResponse(BaseModel):
    conversation_id: str
    session_id: str
    messages: List[ConversationMessage]
    timestamp: datetime
    status: str

class StatusUpdate(BaseModel):
    id: str
    type: str = Field(description="agent_execution, workflow, conversation")
    status: str
    progress: Optional[float] = Field(None, description="Progress percentage 0-100")
    message: Optional[str] = Field(None, description="Status message")
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


# Task 50: Create agent execution API endpoints
@router.post("/execute", response_model=AgentExecutionResponse)
async def execute_agent(
    request: AgentExecutionRequest,
    background_tasks: BackgroundTasks
):
    """
    Execute an AI agent with the specified query and parameters.
    
    Supported agent types:
    - planning: Analyzes query and creates execution plan
    - data_analysis: Performs statistical analysis on data
    - query: Generates and executes database/data queries  
    - insight: Generates business insights and recommendations
    """
    try:
        # Generate execution ID
        execution_id = str(uuid.uuid4())
        
        # Get or create session
        if request.session_id:
            session = await session_manager.get_session(request.session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
        else:
            session = await session_manager.create_session()
            request.session_id = session.session_id
        
        # Validate agent type
        valid_agents = ["planning", "data_analysis", "query", "insight"]
        if request.agent_type not in valid_agents:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid agent type. Supported: {valid_agents}"
            )
        
        # Create execution record
        execution_data = {
            "execution_id": execution_id,
            "agent_type": request.agent_type,
            "query": request.query,
            "data_source": request.data_source,
            "session_id": request.session_id,
            "parameters": request.parameters,
            "status": "pending",
            "timestamp": datetime.now()
        }
        
        # Start agent execution in background
        background_tasks.add_task(
            agent_manager.execute_agent,
            execution_id,
            request.agent_type,
            request.query,
            request.data_source,
            request.parameters
        )
        
        logger.info(f"Started agent execution: {execution_id} (type: {request.agent_type})")
        
        return AgentExecutionResponse(
            execution_id=execution_id,
            agent_type=request.agent_type,
            status="pending",
            session_id=request.session_id,
            timestamp=datetime.now(),
            estimated_duration=30  # Default 30 seconds estimate
        )
        
    except Exception as e:
        logger.error(f"Agent execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")


@router.get("/execution/{execution_id}")
async def get_execution_status(execution_id: str):
    """Get the status of an agent execution."""
    try:
        status = agent_manager.get_execution_status(execution_id)
        if not status:
            raise HTTPException(status_code=404, detail="Execution not found")
        return status
    except Exception as e:
        logger.error(f"Failed to get execution status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Task 51: Implement workflow execution endpoints
@router.post("/workflow/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    request: WorkflowExecutionRequest,
    background_tasks: BackgroundTasks
):
    """
    Execute a multi-step workflow with multiple agents.
    
    Workflow types:
    - data_analysis: Complete data analysis pipeline
    - insight_generation: Generate comprehensive business insights
    - custom: User-defined workflow steps
    """
    try:
        # Generate workflow ID
        workflow_id = str(uuid.uuid4())
        
        # Get or create session
        if request.session_id:
            session = await session_manager.get_session(request.session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
        else:
            session = await session_manager.create_session()
            request.session_id = session.session_id
        
        # Validate workflow type
        valid_workflows = ["data_analysis", "insight_generation", "custom"]
        if request.workflow_type not in valid_workflows:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid workflow type. Supported: {valid_workflows}"
            )
        
        # Start workflow execution in background
        background_tasks.add_task(
            agent_manager.execute_workflow,
            workflow_id,
            request.workflow_type,
            request.steps,
            request.data_source,
            request.session_id
        )
        
        logger.info(f"Started workflow execution: {workflow_id} (type: {request.workflow_type})")
        
        return WorkflowExecutionResponse(
            workflow_id=workflow_id,
            workflow_type=request.workflow_type,
            status="pending",
            session_id=request.session_id,
            steps_total=len(request.steps),
            steps_completed=0,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


@router.get("/workflow/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """Get the status of a workflow execution."""
    try:
        status = agent_manager.get_workflow_status(workflow_id)
        if not status:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return status
    except Exception as e:
        logger.error(f"Failed to get workflow status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Task 52: Add session management for conversations
@router.post("/session", response_model=SessionResponse)
async def create_session(request: SessionCreateRequest):
    """Create a new conversation session."""
    try:
        session = await session_manager.create_session(
            user_id=request.user_id,
            session_name=request.session_name,
            metadata=request.metadata
        )
        
        logger.info(f"Created new session: {session.session_id}")
        return session
        
    except Exception as e:
        logger.error(f"Failed to create session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get session details."""
    try:
        session = await session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except Exception as e:
        logger.error(f"Failed to get session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions", response_model=List[SessionResponse])
async def list_sessions(user_id: Optional[str] = None, limit: int = 50):
    """List sessions, optionally filtered by user."""
    try:
        sessions = await session_manager.list_sessions(user_id=user_id, limit=limit)
        return sessions
    except Exception as e:
        logger.error(f"Failed to list sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and all associated conversations."""
    try:
        await session_manager.delete_session(session_id)
        logger.info(f"Deleted session: {session_id}")
        return {"message": "Session deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Task 53: Create conversation history storage
@router.post("/conversation", response_model=ConversationResponse)
async def create_conversation(request: ConversationRequest):
    """Add a message to a conversation and get agent response."""
    try:
        # Verify session exists
        session = await session_manager.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Create conversation entry
        conversation = await conversation_manager.add_message(
            session_id=request.session_id,
            message=request.message,
            context=request.context
        )
        
        logger.info(f"Added message to conversation: {conversation.conversation_id}")
        return conversation
        
    except Exception as e:
        logger.error(f"Failed to create conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create conversation: {str(e)}")


@router.get("/conversation/{session_id}/history", response_model=List[ConversationMessage])
async def get_conversation_history(
    session_id: str,
    limit: int = 50,
    offset: int = 0
):
    """Get conversation history for a session."""
    try:
        history = await conversation_manager.get_conversation_history(
            session_id=session_id,
            limit=limit,
            offset=offset
        )
        return history
    except Exception as e:
        logger.error(f"Failed to get conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversation/{session_id}")
async def clear_conversation_history(session_id: str):
    """Clear conversation history for a session."""
    try:
        await conversation_manager.clear_conversation_history(session_id)
        logger.info(f"Cleared conversation history for session: {session_id}")
        return {"message": "Conversation history cleared"}
    except Exception as e:
        logger.error(f"Failed to clear conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Task 54: Implement real-time status updates
@router.get("/status/stream/{session_id}")
async def stream_status_updates(session_id: str):
    """Stream real-time status updates for a session via Server-Sent Events."""
    async def generate_status_stream():
        """Generator for status updates."""
        try:
            # Verify session exists
            session = await session_manager.get_session(session_id)
            if not session:
                yield f"data: {json.dumps({'error': 'Session not found'})}\n\n"
                return
            
            # Subscribe to status updates for this session
            async for update in agent_manager.subscribe_to_updates(session_id):
                # Format as Server-Sent Events
                status_data = {
                    "id": update.id,
                    "type": update.type,
                    "status": update.status,
                    "progress": update.progress,
                    "message": update.message,
                    "timestamp": update.timestamp.isoformat(),
                    "metadata": update.metadata
                }
                yield f"data: {json.dumps(status_data)}\n\n"
                
        except Exception as e:
            logger.error(f"Status stream error: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_status_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )


@router.get("/status/{execution_id}")
async def get_status_update(execution_id: str):
    """Get current status of an execution or workflow."""
    try:
        status = agent_manager.get_status_update(execution_id)
        if not status:
            raise HTTPException(status_code=404, detail="Status not found")
        return status
    except Exception as e:
        logger.error(f"Failed to get status update: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def agent_health_check():
    """Health check for agent system."""
    try:
        # Check agent manager health
        agent_health = agent_manager.health_check()
        session_health = await session_manager.health_check()
        conversation_health = await conversation_manager.health_check()
        
        overall_health = all([agent_health, session_health, conversation_health])
        
        return {
            "status": "healthy" if overall_health else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "agent_manager": "healthy" if agent_health else "unhealthy",
                "session_manager": "healthy" if session_health else "unhealthy", 
                "conversation_manager": "healthy" if conversation_health else "unhealthy"
            }
        }
    except Exception as e:
        logger.error(f"Agent health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.websocket("/ws/status/{session_id}")
async def websocket_status_endpoint(websocket: WebSocket, session_id: str):
    """
    Task 54: Provide real-time status updates via WebSocket.
    """
    await websocket.accept()
    try:
        async for update in agent_manager.subscribe_to_updates(session_id):
            await websocket.send_json(asdict(update))
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        await websocket.close(code=1011)
