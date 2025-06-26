# Enterprise Insights Copilot Backend
# FastAPI + LangGraph Multi-Agent AI System

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
import os
from contextlib import asynccontextmanager

from app.api.routes import upload, query, health, sql_direct, agent_status
from app.core.config import settings
from app.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Enterprise Insights Copilot...")
    await init_db()
    print("✅ Database initialized")
    yield
    # Shutdown
    print("🛑 Shutting down Enterprise Insights Copilot...")


app = FastAPI(
    title="Enterprise Insights Copilot",
    description="AI-Powered Business Intelligence Assistant with Multi-Agent Framework",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend-domain.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(upload.router, prefix="/api/v1", tags=["Upload"])
app.include_router(query.router, prefix="/api/v1", tags=["Query"])
app.include_router(sql_direct.router, prefix="/api/v1/query", tags=["SQL Direct"])
app.include_router(agent_status.router, prefix="/api/v1/agents", tags=["Agent Status"])


@app.get("/")
async def root():
    return {
        "message": "Enterprise Insights Copilot API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Simple health check endpoint for frontend"""
    return {
        "status": "healthy",
        "message": "Backend is running"
    }


# Add direct endpoints for frontend compatibility
@app.post("/upload")
async def upload_file_direct(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Direct upload endpoint for frontend compatibility"""
    from app.api.routes.upload import upload_file
    return await upload_file(background_tasks, file)


@app.post("/query") 
async def query_direct(request: dict):
    """Direct query endpoint for frontend compatibility"""
    from app.api.routes.query import process_query
    from app.models.query_models import QueryRequest
    
    query_req = QueryRequest(**request)
    return await process_query(query_req)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
