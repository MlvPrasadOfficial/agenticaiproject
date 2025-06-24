# Data Models for Enterprise Insights Copilot

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class FileUpload(Base):
    __tablename__ = "file_uploads"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    upload_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Data profiling results
    row_count = Column(Integer)
    column_count = Column(Integer)
    column_types = Column(JSON)  # Store column type mapping
    data_profile = Column(JSON)  # Store comprehensive data profile
    
    # Processing status
    is_processed = Column(Boolean, default=False)
    processing_status = Column(String(50), default="pending")
    error_message = Column(Text)


class QuerySession(Base):
    __tablename__ = "query_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True)
    user_query = Column(Text, nullable=False)
    query_type = Column(String(50))
    complexity_score = Column(Float)
    
    # Agent execution results
    planning_result = Column(JSON)
    retrieval_result = Column(JSON)
    data_analysis_result = Column(JSON)
    insight_result = Column(JSON)
    chart_result = Column(JSON)
    narrative_result = Column(JSON)
    final_report = Column(JSON)
    
    # Execution metadata
    execution_time = Column(Float)  # in seconds
    agent_trace = Column(JSON)  # LangSmith trace info
    status = Column(String(50), default="pending")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AgentExecution(Base):
    __tablename__ = "agent_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    agent_name = Column(String(100), nullable=False)
    agent_type = Column(String(50), nullable=False)
    
    # Execution details
    input_data = Column(JSON)
    output_data = Column(JSON)
    execution_time = Column(Float)
    status = Column(String(50))  # success, failed, pending
    error_message = Column(Text)
    
    # Performance metrics
    token_usage = Column(Integer)
    cost_estimate = Column(Float)
    
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))


class DataInsight(Base):
    __tablename__ = "data_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, index=True)  # Foreign key to FileUpload
    insight_type = Column(String(100), nullable=False)
    insight_category = Column(String(50))  # statistical, trend, anomaly, correlation
    
    # Insight content
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    confidence_score = Column(Float)
    statistical_significance = Column(Float)
    
    # Supporting data
    supporting_data = Column(JSON)
    visualization_spec = Column(JSON)
    business_impact = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_validated = Column(Boolean, default=False)


class GeneratedReport(Base):
    __tablename__ = "generated_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    report_title = Column(String(200), nullable=False)
    report_type = Column(String(50))  # executive, detailed, technical
    
    # Report content
    executive_summary = Column(Text)
    key_findings = Column(JSON)
    recommendations = Column(JSON)
    visualizations = Column(JSON)
    full_narrative = Column(Text)
    
    # Metadata
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    report_format = Column(String(20), default="json")  # json, pdf, html
    file_path = Column(String(500))  # Path to generated file
    download_count = Column(Integer, default=0)
