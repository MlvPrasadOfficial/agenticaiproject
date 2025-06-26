# Query Processing API Routes

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from app.services.agent_orchestrator import AgentOrchestrator
from app.models.query_models import QueryRequest, QueryResponse

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process user query through multi-agent system"""
    
    try:
        orchestrator = AgentOrchestrator()
        
        # Generate session ID
        timestamp = request.timestamp if request.timestamp else datetime.now()
        session_id = f"session_{int(timestamp.timestamp())}_{hash(request.query) % 10000}"
        
        # Prepare file context from file_id if provided
        file_context = None
        if hasattr(request, 'file_id') and request.file_id:
            file_context = {"file_id": request.file_id}
        elif request.file_context:
            file_context = request.file_context
        
        print(f"🔍 DEBUG: Processing query: {request.query}")
        print(f"🔍 DEBUG: File context: {file_context}")
        
        # Execute agent workflow
        result = await orchestrator.process_query(
            session_id=session_id,
            user_query=request.query,
            file_context=file_context,
            query_type=request.query_type
        )
        
        print(f"🔍 DEBUG: Orchestrator result: {result}")
        
        return QueryResponse(
            session_id=session_id,
            query=request.query,
            result=result,
            status="completed",
            execution_time=result.get("execution_time", 0),
            agent_trace=result.get("agent_trace", [])
        )
    
    except Exception as e:
        print(f"❌ Query route error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@router.post("/query/stream")
async def stream_query(request: QueryRequest):
    """Stream query processing updates in real-time"""
    
    async def generate_stream():
        try:
            orchestrator = AgentOrchestrator()
            
            # Generate session ID
            session_id = f"session_{request.timestamp}_{hash(request.query) % 10000}"
            
            # Stream agent workflow updates
            async for update in orchestrator.stream_query(
                session_id=session_id,
                user_query=request.query,
                file_context=request.file_context,
                query_type=request.query_type
            ):
                yield f"data: {json.dumps(update)}\n\n"
        
        except Exception as e:
            error_update = {
                "type": "error",
                "message": str(e),
                "timestamp": request.timestamp
            }
            yield f"data: {json.dumps(error_update)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )


@router.get("/query/history")
async def get_query_history(limit: int = 10, offset: int = 0):
    """Get query history with pagination"""
    # Implementation would query database
    return {
        "queries": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }


@router.get("/query/{session_id}")
async def get_query_result(session_id: str):
    """Get detailed results for a specific query session"""
    # Implementation would query database
    return {
        "session_id": session_id,
        "status": "completed",
        "result": {},
        "agent_trace": []
    }


@router.get("/report/{session_id}")
async def download_report(session_id: str, format: str = "pdf"):
    """Download generated report in specified format"""
    
    try:
        orchestrator = AgentOrchestrator()
        
        # Generate report
        report_data = await orchestrator.generate_report(session_id, format)
        
        if not report_data:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Determine content type and filename
        content_types = {
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }
        
        filename = f"insights-report-{session_id}.{format}"
        
        return StreamingResponse(
            iter([report_data]),
            media_type=content_types.get(format, "application/octet-stream"),
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.post("/query/{session_id}/feedback")
async def submit_query_feedback(session_id: str, feedback: Dict[str, Any]):
    """Submit feedback for query results to improve system"""
    # Implementation would save feedback to database
    return {"message": "Feedback submitted successfully"}
