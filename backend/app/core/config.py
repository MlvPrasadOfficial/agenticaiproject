"""
Enterprise Insights Copilot - Configuration Settings
MAANG-level configuration management with Pydantic
"""

from functools import lru_cache
from typing import List, Optional
from pydantic import BaseSettings, validator
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
    
    # AI/LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT: str = "enterprise-insights-copilot"
    
    # Vector Database
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: str = "us-east1-gcp"
    PINECONE_INDEX_NAME: str = "enterprise-insights"
    
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
    
    @validator("ENVIRONMENT", pre=True)
    def validate_environment(cls, v):
        """Validate environment setting"""
        if isinstance(v, str):
            return Environment(v.lower())
        return v
    
    @validator("DEBUG", pre=True)
    def validate_debug(cls, v, values):
        """Auto-set debug based on environment"""
        if "ENVIRONMENT" in values:
            return values["ENVIRONMENT"] == Environment.DEVELOPMENT
        return v
    
    @validator("ALLOWED_HOSTS", pre=True)
    def validate_allowed_hosts(cls, v):
        """Parse allowed hosts from environment"""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v, values):
        """Ensure secret key is set in production"""
        if values.get("ENVIRONMENT") == Environment.PRODUCTION:
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


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
