"""
Enterprise Insights Copilot - Configuration Settings
MAANG-level configuration management with Pydantic
"""

from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator, ValidationInfo
from enum import Enum
import os


class Environment(str, Enum):
    """Environment enumeration"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Log level enumeration"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    PROJECT_NAME: str = "Enterprise Insights Copilot"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "MAANG-level AI-powered business insights platform"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Database
    DATABASE_URL: Optional[str] = None
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: Optional[str] = None
    
    # Logging
    LOG_LEVEL: LogLevel = LogLevel.INFO
    LOG_FORMAT: str = "json"
    LOG_FILE: str = "logs/app.log"
    
    # File Upload
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_FILE_TYPES: List[str] = [".csv", ".xlsx", ".xls", ".json", ".txt"]
    UPLOAD_DIRECTORY: str = "uploads"
    UPLOAD_DIR: str = "uploads"  # For compatibility
    MAX_FILES_PER_UPLOAD: int = 5
    ENABLE_VIRUS_SCANNING: bool = False  # Set to True in production with ClamAV
    ENABLE_FILE_COMPRESSION: bool = True
    
    # AI/LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT: str = "enterprise-insights-copilot"
    
    # Vector Database - Pinecone Configuration
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: str = "us-east1-gcp"
    PINECONE_INDEX_NAME: str = "enterprise-insights"
    PINECONE_HOST: Optional[str] = None
    PINECONE_DIMENSION: int = 384
    PINECONE_METRIC: str = "cosine"
    PINECONE_CLOUD: str = "aws"
    PINECONE_REGION: str = "us-east-1"
    PINECONE_TOP_K: int = 10
    PINECONE_INCLUDE_METADATA: bool = True
    PINECONE_INCLUDE_VALUES: bool = False
    PINECONE_BATCH_SIZE: int = 100
    PINECONE_MAX_RETRIES: int = 3
    PINECONE_TIMEOUT: int = 30
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1:8b"
    OLLAMA_TIMEOUT: int = 120
    OLLAMA_TEMPERATURE: float = 0.7
    OLLAMA_MAX_TOKENS: int = 2048
    
    # LangChain Configuration
    LANGCHAIN_TRACING_V2: bool = True
    LANGCHAIN_PROJECT: str = "enterprise-insights-copilot"
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"
    
    # Application Configuration
    APP_NAME: str = "Enterprise Insights Copilot"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    WORKERS: int = 1
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "https://localhost:3000"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    CORS_HEADERS: List[str] = ["*"]
    
    # File Upload Configuration
    ALLOWED_EXTENSIONS: List[str] = ["csv", "xlsx", "xls", "json", "txt", "pdf"]
    UPLOAD_TIMEOUT: int = 300
    
    # Database Configuration
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_ECHO: bool = False
    
    # Cache Configuration
    CACHE_MAX_SIZE: int = 1000
    
    # Token Configuration
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Logging Configuration
    DETAILED_LOGS: bool = True
    
    # Analytics Configuration
    ENABLE_ANALYTICS: bool = True
    
    # Agent Configuration
    DEFAULT_LLM_MODEL: str = "gpt-4"
    AGENT_TIMEOUT: int = 300  # 5 minutes
    MAX_AGENT_RETRIES: int = 3
    AGENT_TEMPERATURE: float = 0.1
    
    # Monitoring and Observability
    ENABLE_METRICS: bool = True
    ENABLE_TRACING: bool = True
    METRICS_PORT: int = 9090
    JAEGER_ENDPOINT: Optional[str] = None
    
    # Performance
    ENABLE_CACHING: bool = True
    CACHE_TTL: int = 3600  # 1 hour
    REQUEST_TIMEOUT: int = 30
    
    # Feature Flags
    ENABLE_FILE_UPLOAD: bool = True
    ENABLE_DATA_PREVIEW: bool = True
    ENABLE_AI_AGENTS: bool = True
    ENABLE_RAG: bool = True
    
    @field_validator("ENVIRONMENT", mode="before")
    @classmethod
    def validate_environment(cls, v):
        """Validate environment setting"""
        if isinstance(v, str):
            return Environment(v.lower())
        return v
    
    @field_validator("DEBUG", mode="before")
    @classmethod  
    def validate_debug(cls, v, info):
        """Auto-set debug based on environment"""
        if hasattr(info, 'data') and "ENVIRONMENT" in info.data:
            return info.data["ENVIRONMENT"] == Environment.DEVELOPMENT
        return v
    
    @field_validator("CORS_ORIGINS", "CORS_METHODS", "CORS_HEADERS", "ALLOWED_EXTENSIONS", mode="before")
    @classmethod
    def validate_list_fields(cls, v):
        """Parse list fields from environment variables"""
        if isinstance(v, str):
            # Handle JSON-like strings
            if v.startswith('[') and v.endswith(']'):
                import json
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    # Fallback to comma-separated
                    v = v.strip('[]"').replace('"', '')
                    return [item.strip() for item in v.split(',')]
            else:
                return [item.strip() for item in v.split(',')]
        return v

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def validate_allowed_hosts(cls, v):
        """Parse allowed hosts from environment"""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v, info):
        """Ensure secret key is set in production"""
        if hasattr(info, 'data') and info.data.get("ENVIRONMENT") == Environment.PRODUCTION:
            if v == "your-super-secret-key-change-in-production":
                raise ValueError("SECRET_KEY must be set in production")
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.ENVIRONMENT == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.ENVIRONMENT == Environment.PRODUCTION
    
    @property
    def is_staging(self) -> bool:
        """Check if running in staging mode"""
        return self.ENVIRONMENT == Environment.STAGING

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"  # Allow extra fields to prevent validation errors


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
