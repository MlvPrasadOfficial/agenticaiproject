"""
Direct SQL Endpoint - Bypasses orchestration for testing
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
import time
import os
import pandas as pd
import uuid
import json

from app.models.query_models import QueryRequest, QueryResponse
from app.agents.sql_agent import SQLAgent

router = APIRouter()

@router.post("/sql_direct", response_model=dict)
async def process_sql_direct(request: QueryRequest):
    """Process SQL query directly without orchestration"""
    
    try:
        print("🔍 Direct SQL endpoint: Processing query")
        
        # Check for file_id
        file_id = request.file_id
        if not file_id:
            raise HTTPException(
                status_code=400,
                detail="file_id is required for SQL direct endpoint"
            )
        
        # Locate file
        upload_dir = "uploads"  # Relative to backend working directory
        pattern = os.path.join(upload_dir, f"{file_id}_*")
        
        import glob
        matching_files = glob.glob(pattern)
        if not matching_files:
            raise HTTPException(
                status_code=404,
                detail=f"File with ID {file_id} not found"
            )
        
        file_path = matching_files[0]
        print(f"🔍 Direct SQL endpoint: Found file at {file_path}")
        
        # Load data
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
                print(f"🔍 Direct SQL endpoint: Loaded CSV with {len(df)} rows, {len(df.columns)} columns")
                
                # Convert DataFrame to dict
                file_data = {
                    "columns": list(df.columns),
                    "data": df.to_dict('records'),
                    "shape": df.shape,
                    "dtypes": {str(k): str(v) for k, v in df.dtypes.to_dict().items()}
                }
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type for {file_path}"
                )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error loading file: {str(e)}"
            )
        
        # Prepare state for SQL agent
        state = {
            "session_id": f"direct_sql_{uuid.uuid4()}",
            "user_query": request.query,
            "file_context": {"file_id": file_id},
            "file_data": file_data,
            "query_type": "sql"
        }
        
        # Initialize SQL agent
        sql_agent = SQLAgent()
        
        # Execute SQL agent
        start_time = time.time()
        result = await sql_agent.execute(state)
        execution_time = time.time() - start_time
        
        print(f"🔍 Direct SQL endpoint: Query executed in {execution_time:.2f} seconds")
        
        # Add execution info
        result["execution_time"] = execution_time
        return result
        
    except Exception as e:
        print(f"❌ Direct SQL endpoint error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing SQL query: {str(e)}"
        )
