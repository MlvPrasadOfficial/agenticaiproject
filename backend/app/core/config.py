# Core Configuration Settings

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Enterprise Insights Copilot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database Settings
    DATABASE_URL: str = "sqlite:///./enterprise_insights.db"
      # AI/ML Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1"    # Pinecone Settings
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    PINECONE_INDEX_NAME: str = "pineindex"  # Using original index with 1024 dimensions
    PINECONE_HOST: Optional[str] = None
    
    # LangSmith Settings
    LANGCHAIN_TRACING_V2: bool = True
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "enterprise-insights-copilot"
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_FILE_TYPES: list = [".csv", ".xlsx", ".json", ".parquet"]
    UPLOAD_DIRECTORY: str = "./uploads"
    
    # Security Settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Settings
    ALLOWED_ORIGINS: list = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
