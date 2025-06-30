"""
Agent Input/Output Models with Pydantic
Task 101: Implement agent input/output models with Pydantic
"""

from typing import Dict, List, Any, Optional, Union, Literal
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field, validator, root_validator
import uuid

from app.agents.base_agent import AgentCapability, AgentStatus


class DataType(str, Enum):
    """Supported data types for agent I/O"""
    TEXT = "text"
    JSON = "json"
    FILE = "file"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    CSV = "csv"
    EXCEL = "excel"
    PDF = "pdf"
    BINARY = "binary"


class MessageRole(str, Enum):
    """Message roles in conversation"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class ValidationLevel(str, Enum):
    """Input validation levels"""
    STRICT = "strict"      # Strict validation, reject invalid data
    LENIENT = "lenient"    # Accept with warnings
    AUTO_FIX = "auto_fix"  # Attempt to fix invalid data


class OutputFormat(str, Enum):
    """Output format preferences"""
    TEXT = "text"
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    STRUCTURED = "structured"


# Base Models for Agent I/O


class AgentMessage(BaseModel):
    """Individual message in agent communication"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique message ID")
    role: MessageRole = Field(..., description="Role of the message sender")
    content: str = Field(..., min_length=1, description="Message content")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Message timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FileAttachment(BaseModel):
    """File attachment for agent input"""
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type of the file")
    size: int = Field(..., ge=0, description="File size in bytes")
    data_type: DataType = Field(..., description="Interpreted data type")
    file_path: Optional[str] = Field(None, description="Path to stored file")
    file_url: Optional[str] = Field(None, description="URL to access file")
    checksum: Optional[str] = Field(None, description="File checksum for integrity")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="File metadata")
    
    @validator('size')
    def validate_size(cls, v):
        if v > 100 * 1024 * 1024:  # 100MB limit
            raise ValueError("File size too large (max 100MB)")
        return v


class ContextData(BaseModel):
    """Context information for agent processing"""
    session_id: Optional[str] = Field(None, description="Session identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    conversation_history: List[AgentMessage] = Field(default_factory=list, description="Recent conversation")
    domain: Optional[str] = Field(None, description="Domain or topic context")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Processing constraints")
    environment: Dict[str, Any] = Field(default_factory=dict, description="Environment variables")


class ProcessingOptions(BaseModel):
    """Options for agent processing"""
    validation_level: ValidationLevel = Field(default=ValidationLevel.STRICT, description="Input validation level")
    output_format: OutputFormat = Field(default=OutputFormat.TEXT, description="Preferred output format")
    max_tokens: Optional[int] = Field(None, ge=1, le=100000, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="LLM temperature")
    timeout: Optional[int] = Field(None, ge=1, le=3600, description="Processing timeout in seconds")
    include_reasoning: bool = Field(default=False, description="Include reasoning in output")
    include_confidence: bool = Field(default=False, description="Include confidence scores")
    stream_response: bool = Field(default=False, description="Stream response chunks")


# Enhanced Agent Input Model


class AgentInputV2(BaseModel):
    """Enhanced agent input model with comprehensive features"""
    
    # Core input
    message: str = Field(..., min_length=1, max_length=50000, description="Primary input message")
    
    # Message context
    messages: List[AgentMessage] = Field(default_factory=list, description="Conversation messages")
    
    # File attachments
    attachments: List[FileAttachment] = Field(default_factory=list, description="File attachments")
    
    # Context and metadata
    context: ContextData = Field(default_factory=ContextData, description="Processing context")
    
    # Processing options
    options: ProcessingOptions = Field(default_factory=ProcessingOptions, description="Processing options")
    
    # Agent selection
    requested_capabilities: List[AgentCapability] = Field(default_factory=list, description="Required capabilities")
    preferred_agent: Optional[str] = Field(None, description="Preferred agent ID")
    
    # Request metadata
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique request ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Request timestamp")
    priority: int = Field(default=0, ge=-10, le=10, description="Request priority (-10 to 10)")
    
    @validator('attachments')
    def validate_attachments(cls, v):
        if len(v) > 10:  # Max 10 attachments
            raise ValueError("Too many attachments (max 10)")
        
        total_size = sum(att.size for att in v)
        if total_size > 500 * 1024 * 1024:  # 500MB total limit
            raise ValueError("Total attachment size too large (max 500MB)")
        
        return v
    
    @root_validator
    def validate_input(cls, values):
        """Cross-field validation"""
        message = values.get('message', '')
        attachments = values.get('attachments', [])
        
        # Ensure we have some content
        if not message.strip() and not attachments:
            raise ValueError("Must provide either message content or attachments")
        
        return values
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Agent Output Models


class ConfidenceScore(BaseModel):
    """Confidence score for different aspects"""
    overall: float = Field(..., ge=0.0, le=1.0, description="Overall confidence")
    accuracy: Optional[float] = Field(None, ge=0.0, le=1.0, description="Accuracy confidence")
    completeness: Optional[float] = Field(None, ge=0.0, le=1.0, description="Completeness confidence")
    relevance: Optional[float] = Field(None, ge=0.0, le=1.0, description="Relevance confidence")


class ReasoningStep(BaseModel):
    """Individual reasoning step"""
    step_number: int = Field(..., ge=1, description="Step number")
    description: str = Field(..., description="Step description")
    input_data: Optional[Dict[str, Any]] = Field(None, description="Input for this step")
    output_data: Optional[Dict[str, Any]] = Field(None, description="Output from this step")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Step confidence")
    duration: Optional[float] = Field(None, ge=0.0, description="Step duration in seconds")


class PerformanceMetrics(BaseModel):
    """Performance metrics for agent execution"""
    execution_time: float = Field(..., ge=0.0, description="Total execution time in seconds")
    token_usage: Dict[str, int] = Field(default_factory=dict, description="Token usage statistics")
    memory_usage: Optional[int] = Field(None, ge=0, description="Memory usage in bytes")
    api_calls: int = Field(default=0, ge=0, description="Number of API calls made")
    cache_hits: int = Field(default=0, ge=0, description="Number of cache hits")
    cache_misses: int = Field(default=0, ge=0, description="Number of cache misses")


class Citation(BaseModel):
    """Citation for source material"""
    source_id: str = Field(..., description="Source identifier")
    title: Optional[str] = Field(None, description="Source title")
    url: Optional[str] = Field(None, description="Source URL")
    excerpt: Optional[str] = Field(None, description="Relevant excerpt")
    relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Relevance score")


class AgentOutputV2(BaseModel):
    """Enhanced agent output model with comprehensive features"""
    
    # Core response
    response: str = Field(..., description="Primary response content")
    
    # Status and metadata
    status: AgentStatus = Field(..., description="Execution status")
    agent_id: str = Field(..., description="ID of the agent that processed the request")
    request_id: str = Field(..., description="Original request ID")
    
    # Confidence and reasoning
    confidence: Optional[ConfidenceScore] = Field(None, description="Confidence scores")
    reasoning: Optional[List[ReasoningStep]] = Field(None, description="Reasoning process")
    
    # Suggestions and follow-ups
    suggestions: List[str] = Field(default_factory=list, description="Follow-up suggestions")
    related_questions: List[str] = Field(default_factory=list, description="Related questions")
    
    # Citations and sources
    citations: List[Citation] = Field(default_factory=list, description="Source citations")
    
    # Performance metrics
    metrics: PerformanceMetrics = Field(..., description="Performance metrics")
    
    # Generated content metadata
    content_type: DataType = Field(default=DataType.TEXT, description="Response content type")
    content_length: int = Field(..., ge=0, description="Response length in characters")
    language: Optional[str] = Field(None, description="Response language")
    
    # Error handling
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    
    # Timestamps
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Response timestamp")
    
    # Additional data
    structured_data: Optional[Dict[str, Any]] = Field(None, description="Structured response data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('content_length', always=True)
    def set_content_length(cls, v, values):
        """Automatically set content length"""
        response = values.get('response', '')
        return len(response)
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Specialized I/O Models for Different Agent Types


class DataAnalysisInput(AgentInputV2):
    """Specialized input for data analysis agents"""
    data_source: Optional[str] = Field(None, description="Data source identifier")
    analysis_type: Optional[str] = Field(None, description="Type of analysis requested")
    columns_of_interest: List[str] = Field(default_factory=list, description="Specific columns to analyze")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Data filters to apply")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Analyze the sales data for trends and patterns",
                "data_source": "sales_data.csv",
                "analysis_type": "trend_analysis",
                "columns_of_interest": ["date", "sales_amount", "region"],
                "filters": {"region": "North America", "date_range": "2023-01-01:2023-12-31"}
            }
        }


class DataAnalysisOutput(AgentOutputV2):
    """Specialized output for data analysis agents"""
    analysis_results: Dict[str, Any] = Field(default_factory=dict, description="Analysis results")
    visualizations: List[str] = Field(default_factory=list, description="Generated visualization URLs")
    insights: List[str] = Field(default_factory=list, description="Key insights discovered")
    recommendations: List[str] = Field(default_factory=list, description="Data-driven recommendations")
    
    class Config:
        schema_extra = {
            "example": {
                "response": "Analysis of sales data reveals strong seasonal trends...",
                "analysis_results": {"total_sales": 1000000, "growth_rate": 0.15},
                "insights": ["Q4 shows 25% increase", "Western region outperforming"],
                "recommendations": ["Increase inventory for Q4", "Expand in Western region"]
            }
        }


class ConversationInput(AgentInputV2):
    """Specialized input for conversation agents"""
    conversation_type: Optional[str] = Field(None, description="Type of conversation")
    personality: Optional[str] = Field(None, description="Desired personality traits")
    tone: Optional[str] = Field(None, description="Desired tone of response")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Tell me about the weather today",
                "conversation_type": "casual",
                "personality": "friendly",
                "tone": "helpful"
            }
        }


class ConversationOutput(AgentOutputV2):
    """Specialized output for conversation agents"""
    conversation_state: Dict[str, Any] = Field(default_factory=dict, description="Current conversation state")
    emotion_detected: Optional[str] = Field(None, description="Detected user emotion")
    intent: Optional[str] = Field(None, description="Detected user intent")
    
    class Config:
        schema_extra = {
            "example": {
                "response": "Today's weather is sunny with a high of 75°F...",
                "emotion_detected": "curious",
                "intent": "weather_inquiry"
            }
        }


# Validation Utilities


class InputValidator:
    """Utility class for validating agent inputs"""
    
    @staticmethod
    def validate_text_length(text: str, min_length: int = 1, max_length: int = 50000) -> bool:
        """Validate text length"""
        return min_length <= len(text) <= max_length
    
    @staticmethod
    def validate_file_type(filename: str, allowed_types: List[str]) -> bool:
        """Validate file type by extension"""
        extension = filename.lower().split('.')[-1]
        return extension in allowed_types
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize input text"""
        # Remove potentially harmful content
        # This is a basic implementation - would need more sophisticated sanitization
        import re
        
        # Remove script tags and similar
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @staticmethod
    def validate_request_rate(user_id: str, max_requests_per_minute: int = 60) -> bool:
        """Validate request rate (basic implementation)"""
        # In a real implementation, this would check against a rate limiting store
        # For now, just return True
        return True


# Factory for creating appropriate I/O models


class IOModelFactory:
    """Factory for creating appropriate I/O models based on agent type"""
    
    INPUT_MODELS = {
        AgentCapability.DATA_ANALYSIS: DataAnalysisInput,
        AgentCapability.CONVERSATION: ConversationInput,
        # Add more specialized models as needed
    }
    
    OUTPUT_MODELS = {
        AgentCapability.DATA_ANALYSIS: DataAnalysisOutput,
        AgentCapability.CONVERSATION: ConversationOutput,
        # Add more specialized models as needed
    }
    
    @classmethod
    def create_input_model(cls, capability: AgentCapability, **kwargs) -> AgentInputV2:
        """Create appropriate input model for agent capability"""
        model_class = cls.INPUT_MODELS.get(capability, AgentInputV2)
        return model_class(**kwargs)
    
    @classmethod
    def create_output_model(cls, capability: AgentCapability, **kwargs) -> AgentOutputV2:
        """Create appropriate output model for agent capability"""
        model_class = cls.OUTPUT_MODELS.get(capability, AgentOutputV2)
        return model_class(**kwargs)
    
    @classmethod
    def register_models(cls, capability: AgentCapability, input_model: type, output_model: type):
        """Register custom I/O models for a capability"""
        cls.INPUT_MODELS[capability] = input_model
        cls.OUTPUT_MODELS[capability] = output_model
