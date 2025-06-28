# ⚡ Backend Architecture
## Enterprise Insights Copilot - FastAPI Backend Implementation

### 🏗️ Architecture Overview

The backend follows a **clean architecture pattern** with FastAPI, implementing domain-driven design principles and clear separation of concerns.

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config/                 # Configuration management
│   │   ├── __init__.py
│   │   ├── settings.py         # Pydantic settings
│   │   └── logging.py          # Logging configuration
│   ├── core/                   # Core business logic
│   │   ├── __init__.py
│   │   ├── dependencies.py     # Dependency injection
│   │   ├── middleware.py       # Custom middleware
│   │   └── security.py         # Authentication/authorization
│   ├── api/                    # API layer
│   │   ├── __init__.py
│   │   ├── v1/                 # API version 1
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/      # Route handlers
│   │   │   └── dependencies.py # Route dependencies
│   ├── models/                 # Data models
│   │   ├── __init__.py
│   │   ├── base.py            # Base model classes
│   │   ├── user.py            # User models
│   │   └── file.py            # File models
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── base.py            # Base schemas
│   │   ├── user.py            # User schemas
│   │   └── file.py            # File schemas
│   ├── services/               # Business logic services
│   │   ├── __init__.py
│   │   ├── file_service.py    # File processing
│   │   ├── data_service.py    # Data analysis
│   │   └── ai_service.py      # AI/ML operations
│   ├── db/                     # Database layer
│   │   ├── __init__.py
│   │   ├── base.py            # Database configuration
│   │   ├── session.py         # Session management
│   │   └── repositories/      # Data access layer
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       ├── logging.py         # Logging utilities
│       └── helpers.py         # Helper functions
├── tests/                      # Test suite
├── requirements.txt            # Python dependencies
├── alembic.ini                # Database migrations
└── Dockerfile                 # Container configuration
```

---

## 🔧 Technology Stack

### Core Framework
- **FastAPI 0.104+**: Modern, fast web framework
- **Python 3.11+**: Latest Python features and performance
- **Uvicorn**: ASGI server with high performance
- **Pydantic 2.0**: Data validation and serialization

### Database & ORM
- **SQLAlchemy 2.0**: Async ORM with modern patterns
- **Alembic**: Database migration management
- **PostgreSQL**: Production database
- **SQLite**: Development database

### AI/ML Stack
- **LangChain**: LLM orchestration framework
- **LangGraph**: Agent workflow management
- **OpenAI API**: GPT-4 integration
- **Pinecone**: Vector database for RAG

### Observability
- **Prometheus**: Metrics collection
- **OpenTelemetry**: Distributed tracing
- **Structured Logging**: JSON-formatted logs
- **Sentry**: Error tracking (optional)

---

## 🚀 Application Setup

### Main Application (main.py)
```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

from app.config.settings import get_settings
from app.config.logging import setup_logging
from app.core.middleware import (
    RequestIDMiddleware,
    LoggingMiddleware,
    ErrorHandlingMiddleware
)
from app.api.v1 import api_router

# Initialize settings and logging
settings = get_settings()
setup_logging(settings.log_level)

# Create FastAPI application
app = FastAPI(
    title="Enterprise Insights Copilot API",
    description="AI-powered data analytics platform",
    version="1.0.0",
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url="/redoc" if settings.environment != "production" else None,
)

# Add middleware (order matters!)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(LoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Health check endpoints
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.environment == "development",
        log_config=None  # Use our custom logging
    )
```

### Configuration Management
```python
# config/settings.py
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Application
    app_name: str = "Enterprise Insights Copilot"
    environment: str = "development"
    debug: bool = False
    port: int = 8000
    
    # Security
    secret_key: str
    allowed_origins: List[str] = ["http://localhost:3000"]
    allowed_hosts: List[str] = ["*"]
    
    # Database
    database_url: str = "sqlite:///./app.db"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # AI/ML
    openai_api_key: Optional[str] = None
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    
    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    upload_directory: str = "./uploads"
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Redis (for caching)
    redis_url: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

---

## 🛡️ Middleware Architecture

### Custom Middleware Stack
```python
# core/middleware.py
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(
            "Request started",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "method": request.method,
                "url": str(request.url),
                "user_agent": request.headers.get("user-agent"),
            }
        )
        
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            "Request completed",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "status_code": response.status_code,
                "process_time": round(process_time, 4),
            }
        )
        
        response.headers["X-Process-Time"] = str(process_time)
        return response

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            logger.exception(
                "Unhandled exception",
                extra={
                    "request_id": getattr(request.state, "request_id", None),
                    "exception_type": type(exc).__name__,
                    "exception_message": str(exc),
                }
            )
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "request_id": getattr(request.state, "request_id", None),
                }
            )
```

---

## 📊 Data Models & Schemas

### SQLAlchemy Models
```python
# models/base.py
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# models/file.py
from sqlalchemy import Column, String, Integer, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
import enum

class FileStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class File(BaseModel):
    __tablename__ = "files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_path = Column(String(500), nullable=False)
    status = Column(Enum(FileStatus), default=FileStatus.PENDING)
    metadata = Column(Text)  # JSON metadata
    user_id = Column(UUID(as_uuid=True), nullable=True)  # For future auth
```

### Pydantic Schemas
```python
# schemas/file.py
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from models.file import FileStatus

class FileBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    size: int = Field(..., gt=0)
    mime_type: str = Field(..., min_length=1)

class FileCreate(FileBase):
    original_name: str
    file_path: str
    
    @validator('size')
    def validate_file_size(cls, v):
        max_size = 10 * 1024 * 1024  # 10MB
        if v > max_size:
            raise ValueError(f'File size cannot exceed {max_size} bytes')
        return v

class FileResponse(FileBase):
    id: UUID
    status: FileStatus
    created_at: datetime
    updated_at: Optional[datetime]
    metadata: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True

class FileUploadResponse(BaseModel):
    file: FileResponse
    upload_id: str
    status: FileStatus
    message: Optional[str] = None
```

---

## 🔄 Service Layer Architecture

### File Service
```python
# services/file_service.py
import os
import aiofiles
import pandas as pd
from typing import BinaryIO, Dict, Any, Optional
from uuid import uuid4
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file import File, FileStatus
from app.schemas.file import FileCreate, FileResponse
from app.config.settings import get_settings

settings = get_settings()

class FileService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def upload_file(self, file: UploadFile) -> FileResponse:
        """Handle file upload with validation and storage."""
        
        # Validate file
        self._validate_file(file)
        
        # Generate unique filename
        file_id = str(uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{file_id}{file_extension}"
        file_path = os.path.join(settings.upload_directory, unique_filename)
        
        # Ensure upload directory exists
        os.makedirs(settings.upload_directory, exist_ok=True)
        
        try:
            # Save file to disk
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Extract metadata
            metadata = await self._extract_metadata(file_path, file.content_type)
            
            # Create database record
            file_create = FileCreate(
                name=unique_filename,
                original_name=file.filename,
                size=len(content),
                mime_type=file.content_type,
                file_path=file_path
            )
            
            db_file = File(**file_create.model_dump())
            db_file.metadata = metadata
            
            self.db.add(db_file)
            await self.db.commit()
            await self.db.refresh(db_file)
            
            return FileResponse.model_validate(db_file)
            
        except Exception as e:
            # Cleanup file on error
            if os.path.exists(file_path):
                os.remove(file_path)
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    
    def _validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file."""
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        allowed_types = [
            "text/csv",
            "application/json",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel"
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file.content_type} not allowed"
            )
    
    async def _extract_metadata(self, file_path: str, content_type: str) -> Dict[str, Any]:
        """Extract metadata from uploaded file."""
        metadata = {}
        
        try:
            if content_type == "text/csv":
                df = pd.read_csv(file_path, nrows=100)  # Sample for metadata
                metadata = {
                    "columns": df.columns.tolist(),
                    "sample_rows": len(df),
                    "dtypes": df.dtypes.astype(str).to_dict(),
                    "null_counts": df.isnull().sum().to_dict(),
                }
            elif content_type == "application/json":
                with open(file_path, 'r') as f:
                    import json
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        metadata = {
                            "record_count": len(data),
                            "sample_keys": list(data[0].keys()) if data else [],
                        }
        except Exception as e:
            metadata["extraction_error"] = str(e)
        
        return metadata
```

### Data Service
```python
# services/data_service.py
import pandas as pd
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.file import File
from app.schemas.data import DataPreviewResponse, DataStatistics

class DataService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_data_preview(
        self,
        file_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> DataPreviewResponse:
        """Get paginated data preview."""
        
        # Get file from database
        file = await self.db.get(File, file_id)
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Load data based on file type
        df = self._load_dataframe(file.file_path, file.mime_type)
        
        # Apply pagination
        total_rows = len(df)
        paginated_df = df.iloc[offset:offset + limit]
        
        # Convert to records
        records = paginated_df.to_dict('records')
        columns = [{"name": col, "type": str(df[col].dtype)} for col in df.columns]
        
        return DataPreviewResponse(
            data=records,
            columns=columns,
            total_rows=total_rows,
            page_size=limit,
            offset=offset
        )
    
    async def get_data_statistics(self, file_id: str) -> DataStatistics:
        """Generate comprehensive data statistics."""
        
        file = await self.db.get(File, file_id)
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        df = self._load_dataframe(file.file_path, file.mime_type)
        
        # Generate statistics
        stats = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "memory_usage": df.memory_usage(deep=True).sum(),
            "numeric_columns": len(df.select_dtypes(include='number').columns),
            "categorical_columns": len(df.select_dtypes(include='object').columns),
            "null_percentage": (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
        }
        
        # Column-level statistics
        column_stats = []
        for col in df.columns:
            col_stat = {
                "name": col,
                "type": str(df[col].dtype),
                "null_count": df[col].isnull().sum(),
                "unique_count": df[col].nunique(),
            }
            
            if df[col].dtype in ['int64', 'float64']:
                col_stat.update({
                    "mean": df[col].mean(),
                    "median": df[col].median(),
                    "std": df[col].std(),
                    "min": df[col].min(),
                    "max": df[col].max(),
                })
            
            column_stats.append(col_stat)
        
        return DataStatistics(
            summary=stats,
            columns=column_stats
        )
    
    def _load_dataframe(self, file_path: str, mime_type: str) -> pd.DataFrame:
        """Load file into pandas DataFrame."""
        try:
            if mime_type == "text/csv":
                return pd.read_csv(file_path)
            elif mime_type == "application/json":
                return pd.read_json(file_path)
            elif mime_type in [
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/vnd.ms-excel"
            ]:
                return pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file type: {mime_type}")
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to load data: {str(e)}"
            )
```

---

## 🛣️ API Routing

### API Router Structure
```python
# api/v1/__init__.py
from fastapi import APIRouter
from .endpoints import files, data, health, ai

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(data.router, prefix="/data", tags=["data"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
```

### File Upload Endpoints
```python
# api/v1/endpoints/files.py
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.dependencies import get_db
from app.services.file_service import FileService
from app.schemas.file import FileUploadResponse

router = APIRouter()

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload and process a data file."""
    file_service = FileService(db)
    
    try:
        result = await file_service.upload_file(file)
        return FileUploadResponse(
            file=result,
            upload_id=str(result.id),
            status=result.status,
            message="File uploaded successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get file information."""
    file = await db.get(File, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse.model_validate(file)

@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a file and its data."""
    file_service = FileService(db)
    await file_service.delete_file(file_id)
    return {"message": "File deleted successfully"}
```

---

## 🔒 Security Implementation

### Authentication & Authorization
```python
# core/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config.settings import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

# Dependency for protected routes
async def get_current_user(user_id: str = Depends(verify_token)):
    # In a real app, fetch user from database
    return {"id": user_id}
```

---

## 📊 Monitoring & Observability

### Prometheus Metrics
```python
# utils/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections'
)

FILE_UPLOADS = Counter(
    'file_uploads_total',
    'Total file uploads',
    ['file_type', 'status']
)

def record_request_metrics(method: str, endpoint: str, status_code: int, duration: float):
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)
```

### Structured Logging
```python
# config/logging.py
import logging
import sys
from typing import Dict, Any
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)

def setup_logging(log_level: str = "INFO"):
    """Configure structured logging."""
    
    # Create formatter
    formatter = JSONFormatter()
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Configure third-party loggers
    logging.getLogger("uvicorn.access").disabled = True
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
```

---

This backend architecture provides a robust, scalable foundation for enterprise-grade applications with proper separation of concerns, comprehensive error handling, and observability features.
