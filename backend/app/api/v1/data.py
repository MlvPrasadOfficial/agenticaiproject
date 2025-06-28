"""
Data Preview and Analysis API endpoints.
Implements Tasks 71-80: Data preview, statistics, filtering, and export functionality.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pandas as pd
from pathlib import Path
import json
import logging

from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.data_processor import data_processor, DataProfile

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api/v1/data", tags=["Data Analysis"])

class DataPreviewResponse(BaseModel):
    file_id: str
    filename: str
    total_rows: int
    total_columns: int
    preview_rows: int
    columns: List[Dict[str, Any]]
    data: List[Dict[str, Any]]
    has_more: bool

class DataStatisticsResponse(BaseModel):
    file_id: str
    filename: str
    overall_stats: Dict[str, Any]
    column_statistics: List[Dict[str, Any]]
    data_quality: Dict[str, Any]
    recommendations: List[str]

class ColumnAnalysisResponse(BaseModel):
    column_name: str
    data_type: str
    statistics: Dict[str, Any]
    quality_score: float
    issues: List[str]
    value_distribution: List[Dict[str, Any]]

@router.get("/preview/{file_id}", response_model=DataPreviewResponse)
async def get_data_preview(
    file_id: str,
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(50, ge=1, le=1000, description="Number of rows per page"),
    columns: Optional[str] = Query(None, description="Comma-separated column names to include")
):
    """
    Get paginated data preview with optional column filtering.
    
    Features:
    - Pagination support for large datasets
    - Column selection
    - Data type information
    - Memory-efficient processing
    """
    
    logger.info(f"Data preview requested for file_id: {file_id}, page: {page}, page_size: {page_size}")
    
    try:
        # Find the file
        file_path = await _find_file_by_id(file_id)
        if not file_path:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Load data efficiently
        df = await _load_data_for_preview(file_path, page, page_size, columns)
        
        # Get total row count efficiently
        total_rows = await _get_total_row_count(file_path)
        
        # Calculate pagination info
        start_row = (page - 1) * page_size
        end_row = min(start_row + page_size, total_rows)
        has_more = end_row < total_rows
        
        # Prepare column information
        column_info = []
        for col in df.columns:
            col_info = {
                "name": col,
                "type": str(df[col].dtype),
                "null_count": int(df[col].isnull().sum()),
                "sample_values": df[col].dropna().head(3).tolist()
            }
            column_info.append(col_info)
        
        # Convert data to JSON-serializable format
        preview_data = []
        for _, row in df.iterrows():
            row_dict = {}
            for col, val in row.items():
                row_dict[col] = _serialize_value(val)
            preview_data.append(row_dict)
        
        response = DataPreviewResponse(
            file_id=file_id,
            filename=file_path.name,
            total_rows=total_rows,
            total_columns=len(df.columns),
            preview_rows=len(preview_data),
            columns=column_info,
            data=preview_data,
            has_more=has_more
        )
        
        logger.info(f"Data preview generated: {len(preview_data)} rows, {len(df.columns)} columns")
        return response
        
    except Exception as e:
        logger.error(f"Data preview failed for file_id {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate data preview: {str(e)}")

@router.get("/statistics/{file_id}", response_model=DataStatisticsResponse)
async def get_data_statistics(file_id: str):
    """
    Get comprehensive data statistics and quality metrics.
    
    Features:
    - Overall dataset statistics
    - Per-column analysis
    - Data quality assessment
    - Actionable recommendations
    """
    
    logger.info(f"Data statistics requested for file_id: {file_id}")
    
    try:
        # Find the file
        file_path = await _find_file_by_id(file_id)
        if not file_path:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Process data to get comprehensive profile
        data_profile = await data_processor.process_file(file_path, file_id)
        
        # Overall statistics
        overall_stats = {
            "row_count": data_profile.row_count,
            "column_count": data_profile.column_count,
            "memory_usage_mb": round(data_profile.memory_usage / (1024 * 1024), 2),
            "processing_time_seconds": data_profile.processing_time,
            "column_type_distribution": {
                "numeric": data_profile.numeric_columns,
                "categorical": data_profile.categorical_columns,
                "datetime": data_profile.datetime_columns,
                "text": data_profile.text_columns
            }
        }
        
        # Column statistics
        column_stats = []
        for col_profile in data_profile.columns:
            col_stat = {
                "name": col_profile.name,
                "data_type": col_profile.data_type,
                "null_count": col_profile.null_count,
                "null_percentage": col_profile.null_percentage,
                "unique_count": col_profile.unique_count,
                "unique_percentage": col_profile.unique_percentage,
                "memory_usage": col_profile.memory_usage,
                "quality_score": col_profile.quality_score,
                "statistics": col_profile.statistics,
                "most_common_values": col_profile.most_common_values[:5]  # Top 5
            }
            column_stats.append(col_stat)
        
        # Data quality summary
        data_quality = {
            "overall_quality": data_profile.overall_quality,
            "quality_score": data_profile.quality_score,
            "issues": data_profile.data_issues
        }
        
        response = DataStatisticsResponse(
            file_id=file_id,
            filename=data_profile.filename,
            overall_stats=overall_stats,
            column_statistics=column_stats,
            data_quality=data_quality,
            recommendations=data_profile.recommendations
        )
        
        logger.info(f"Data statistics generated for {file_id}. Quality: {data_profile.overall_quality}")
        return response
        
    except Exception as e:
        logger.error(f"Data statistics failed for file_id {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate statistics: {str(e)}")

@router.get("/column-analysis/{file_id}/{column_name}", response_model=ColumnAnalysisResponse)
async def get_column_analysis(file_id: str, column_name: str):
    """
    Get detailed analysis for a specific column.
    
    Features:
    - Detailed column statistics
    - Value distribution analysis
    - Quality assessment
    - Data patterns detection
    """
    
    logger.info(f"Column analysis requested for file_id: {file_id}, column: {column_name}")
    
    try:
        # Find the file
        file_path = await _find_file_by_id(file_id)
        if not file_path:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Process data to get profile
        data_profile = await data_processor.process_file(file_path, file_id)
        
        # Find the specific column profile
        column_profile = None
        for col_profile in data_profile.columns:
            if col_profile.name == column_name:
                column_profile = col_profile
                break
        
        if not column_profile:
            raise HTTPException(status_code=404, detail=f"Column '{column_name}' not found")
        
        # Generate value distribution (top 20 values)
        value_distribution = []
        for value, count in column_profile.most_common_values[:20]:
            distribution_item = {
                "value": value,
                "count": count,
                "percentage": round((count / data_profile.row_count) * 100, 2)
            }
            value_distribution.append(distribution_item)
        
        response = ColumnAnalysisResponse(
            column_name=column_profile.name,
            data_type=column_profile.data_type,
            statistics=column_profile.statistics,
            quality_score=column_profile.quality_score,
            issues=column_profile.quality_issues,
            value_distribution=value_distribution
        )
        
        logger.info(f"Column analysis completed for {column_name}")
        return response
        
    except Exception as e:
        logger.error(f"Column analysis failed for {file_id}/{column_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze column: {str(e)}")

@router.get("/search/{file_id}")
async def search_data(
    file_id: str,
    query: str = Query(..., description="Search query"),
    columns: Optional[str] = Query(None, description="Comma-separated column names to search in"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results")
):
    """
    Search data with text matching across specified columns.
    
    Features:
    - Full-text search across columns
    - Column-specific search
    - Case-insensitive matching
    - Result limiting
    """
    
    logger.info(f"Data search requested for file_id: {file_id}, query: '{query}'")
    
    try:
        # Find the file
        file_path = await _find_file_by_id(file_id)
        if not file_path:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Load data
        df = pd.read_csv(file_path) if file_path.suffix.lower() == '.csv' else pd.read_excel(file_path)
        
        # Determine search columns
        search_columns = df.columns.tolist()
        if columns:
            requested_columns = [col.strip() for col in columns.split(',')]
            search_columns = [col for col in requested_columns if col in df.columns]
        
        # Perform search
        mask = pd.Series([False] * len(df))
        query_lower = query.lower()
        
        for col in search_columns:
            if df[col].dtype == 'object':  # Text columns
                col_mask = df[col].astype(str).str.lower().str.contains(query_lower, na=False)
                mask = mask | col_mask
        
        # Apply mask and limit results
        results_df = df[mask].head(limit)
        
        # Convert to JSON-serializable format
        results = []
        for _, row in results_df.iterrows():
            row_dict = {}
            for col, val in row.items():
                row_dict[col] = _serialize_value(val)
            results.append(row_dict)
        
        response = {
            "file_id": file_id,
            "query": query,
            "search_columns": search_columns,
            "total_matches": int(mask.sum()),
            "returned_results": len(results),
            "results": results
        }
        
        logger.info(f"Search completed: {mask.sum()} matches found, {len(results)} returned")
        return response
        
    except Exception as e:
        logger.error(f"Data search failed for file_id {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/export/{file_id}")
async def export_data(
    file_id: str,
    format: str = Query("csv", description="Export format: csv, json, excel"),
    columns: Optional[str] = Query(None, description="Comma-separated column names to export"),
    filters: Optional[str] = Query(None, description="JSON string of filters to apply")
):
    """
    Export data in various formats with optional filtering.
    
    Features:
    - Multiple export formats
    - Column selection
    - Basic filtering
    - Efficient processing
    """
    
    logger.info(f"Data export requested for file_id: {file_id}, format: {format}")
    
    try:
        # Find the file
        file_path = await _find_file_by_id(file_id)
        if not file_path:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Load data
        df = pd.read_csv(file_path) if file_path.suffix.lower() == '.csv' else pd.read_excel(file_path)
        
        # Apply column selection
        if columns:
            requested_columns = [col.strip() for col in columns.split(',')]
            available_columns = [col for col in requested_columns if col in df.columns]
            if available_columns:
                df = df[available_columns]
        
        # Apply filters (basic implementation)
        if filters:
            try:
                filter_dict = json.loads(filters)
                for col, value in filter_dict.items():
                    if col in df.columns:
                        if isinstance(value, list):
                            df = df[df[col].isin(value)]
                        else:
                            df = df[df[col] == value]
            except Exception as filter_error:
                logger.warning(f"Filter application failed: {filter_error}")
        
        # Export based on format
        export_filename = f"{file_id}_export"
        
        if format.lower() == "csv":
            export_data = df.to_csv(index=False)
            media_type = "text/csv"
            export_filename += ".csv"
        elif format.lower() == "json":
            export_data = df.to_json(orient='records', indent=2)
            media_type = "application/json"
            export_filename += ".json"
        elif format.lower() == "excel":
            # For Excel, we'd need to use BytesIO, but for simplicity, convert to CSV
            export_data = df.to_csv(index=False)
            media_type = "text/csv"
            export_filename += ".csv"
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")
        
        logger.info(f"Data export completed: {len(df)} rows, {len(df.columns)} columns")
        
        return JSONResponse(
            content={
                "file_id": file_id,
                "export_format": format,
                "row_count": len(df),
                "column_count": len(df.columns),
                "filename": export_filename,
                "data": export_data
            }
        )
        
    except Exception as e:
        logger.error(f"Data export failed for file_id {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

# Helper functions

async def _find_file_by_id(file_id: str) -> Optional[Path]:
    """Find uploaded file by ID."""
    upload_dir = Path(settings.UPLOAD_DIR)
    
    # Search through upload sessions
    for session_dir in upload_dir.iterdir():
        if session_dir.is_dir():
            for file_path in session_dir.iterdir():
                if file_path.name.startswith(file_id):
                    return file_path
    
    return None

async def _load_data_for_preview(file_path: Path, page: int, page_size: int, columns: Optional[str]) -> pd.DataFrame:
    """Load data efficiently for preview with pagination."""
    skip_rows = (page - 1) * page_size
    
    # Parse column selection
    selected_columns = None
    if columns:
        selected_columns = [col.strip() for col in columns.split(',')]
    
    if file_path.suffix.lower() == '.csv':
        df = pd.read_csv(
            file_path, 
            skiprows=range(1, skip_rows + 1) if skip_rows > 0 else None,
            nrows=page_size,
            usecols=selected_columns,
            low_memory=False
        )
    else:
        # For Excel files, load all then slice (less efficient but simpler)
        full_df = pd.read_excel(file_path, usecols=selected_columns)
        end_row = skip_rows + page_size
        df = full_df.iloc[skip_rows:end_row]
    
    return df

async def _get_total_row_count(file_path: Path) -> int:
    """Get total row count efficiently."""
    try:
        if file_path.suffix.lower() == '.csv':
            # Count lines in CSV (subtract 1 for header)
            with open(file_path, 'r', encoding='utf-8') as f:
                return sum(1 for line in f) - 1
        else:
            # For Excel, we need to load to count
            df = pd.read_excel(file_path, usecols=[0])  # Load only first column
            return len(df)
    except Exception:
        return 0

def _serialize_value(value):
    """Serialize value for JSON compatibility."""
    import pandas as pd
    import numpy as np
    from datetime import datetime
    
    if pd.isna(value):
        return None
    elif isinstance(value, (np.integer, int)):
        return int(value)
    elif isinstance(value, (np.floating, float)):
        return float(value)
    elif isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()
    else:
        return str(value)
