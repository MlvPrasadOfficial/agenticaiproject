# Pydantic Models for API Requests and Responses

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class QueryRequest(BaseModel):
    query: str = Field(..., description="User's natural language query")
    file_id: Optional[str] = Field(None, description="File ID for data context")
    query_type: Optional[str] = Field(None, description="Type of query: analysis, visualization, insight")
    file_context: Optional[Dict[str, Any]] = Field(None, description="File context information")
    timestamp: Optional[datetime] = Field(default_factory=lambda: datetime.now())
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Show me the sales trends for the last quarter",
                "file_id": "file_123",
                "query_type": "analysis",
                "file_context": {"file_id": "file_123", "file_name": "sales_data.csv"}
            }
        }


class QueryResponse(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    query: str = Field(..., description="Original user query")
    result: Dict[str, Any] = Field(..., description="Processing results")
    status: str = Field(..., description="Query processing status")
    execution_time: float = Field(..., description="Execution time in seconds")
    agent_trace: List[Dict[str, Any]] = Field(default=[], description="Agent execution trace")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_123456",
                "query": "Show me the sales trends",
                "result": {
                    "insights": ["Sales increased by 15% in Q3"],
                    "charts": [{"type": "line", "data": []}],
                    "narrative": "Sales performance analysis..."
                },
                "status": "completed",
                "execution_time": 12.5,
                "agent_trace": []
            }
        }


class FileUploadResponse(BaseModel):
    file_id: str = Field(..., description="Unique file identifier")
    filename: str = Field(..., description="Original filename")
    size: int = Field(..., description="File size in bytes")
    status: str = Field(..., description="Upload processing status")
    basic_info: Dict[str, Any] = Field(..., description="Basic file information")
    processing_url: str = Field(..., description="URL to check processing status")


class DataProfile(BaseModel):
    row_count: int = Field(..., description="Number of rows in dataset")
    column_count: int = Field(..., description="Number of columns in dataset")
    column_types: Dict[str, str] = Field(..., description="Column name to data type mapping")
    missing_values: Dict[str, int] = Field(..., description="Missing value counts per column")
    data_quality_score: float = Field(..., description="Overall data quality score 0-1")
    summary_statistics: Dict[str, Any] = Field(..., description="Statistical summaries")
    
    class Config:
        json_schema_extra = {
            "example": {
                "row_count": 1000,
                "column_count": 5,
                "column_types": {"sales": "numeric", "date": "datetime", "region": "categorical"},
                "missing_values": {"sales": 5, "region": 0},
                "data_quality_score": 0.95,
                "summary_statistics": {}
            }
        }


class AgentExecutionUpdate(BaseModel):
    agent_name: str = Field(..., description="Name of the executing agent")
    status: str = Field(..., description="Agent execution status")
    progress: float = Field(..., description="Progress percentage 0-100")
    message: str = Field(..., description="Current activity description")
    result: Optional[Dict[str, Any]] = Field(None, description="Agent result if completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    timestamp: datetime = Field(default_factory=datetime.now)


class InsightModel(BaseModel):
    insight_type: str = Field(..., description="Type of insight: trend, anomaly, correlation")
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Detailed insight description")
    confidence_score: float = Field(..., description="Confidence score 0-1")
    business_impact: Optional[str] = Field(None, description="Business impact assessment")
    supporting_data: Dict[str, Any] = Field(..., description="Supporting statistical data")
    visualization: Optional[Dict[str, Any]] = Field(None, description="Visualization specification")


class ChartSpecification(BaseModel):
    chart_type: str = Field(..., description="Type of chart: bar, line, scatter, etc.")
    title: str = Field(..., description="Chart title")
    data: List[Dict[str, Any]] = Field(..., description="Chart data")
    x_axis: str = Field(..., description="X-axis column")
    y_axis: str = Field(..., description="Y-axis column")
    color_column: Optional[str] = Field(None, description="Column for color encoding")
    filters: Optional[Dict[str, Any]] = Field(None, description="Applied filters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "chart_type": "line",
                "title": "Sales Trends Over Time",
                "data": [{"date": "2023-01", "sales": 1000}],
                "x_axis": "date",
                "y_axis": "sales",
                "color_column": "region"
            }
        }


class ReportModel(BaseModel):
    report_id: str = Field(..., description="Unique report identifier")
    title: str = Field(..., description="Report title")
    executive_summary: str = Field(..., description="Executive summary")
    key_findings: List[str] = Field(..., description="Key findings list")
    insights: List[InsightModel] = Field(..., description="Generated insights")
    charts: List[ChartSpecification] = Field(..., description="Generated charts")
    recommendations: List[str] = Field(..., description="Business recommendations")
    generated_at: datetime = Field(default_factory=datetime.now)
    report_type: str = Field(default="comprehensive", description="Type of report")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now)
