"""
Pinecone Vector Database Configuration
Enterprise Insights Copilot - RAG System
"""

import os
from typing import Optional, Dict, Any, List
from pydantic import Field, validator
from pydantic_settings import BaseSettings
import pinecone
from pinecone import Pinecone, ServerlessSpec
import logging

logger = logging.getLogger(__name__)

class PineconeSettings(BaseSettings):
    """Pinecone configuration settings"""
    
    # API Configuration
    api_key: Optional[str] = Field(None, env="PINECONE_API_KEY")
    environment: str = Field("us-east-1-aws", env="PINECONE_ENVIRONMENT")
    
    # Index Configuration
    index_name: str = Field("enterprise-insights", env="PINECONE_INDEX_NAME")
    dimension: int = Field(384, env="PINECONE_DIMENSION")  # sentence-transformers/all-MiniLM-L6-v2
    metric: str = Field("cosine", env="PINECONE_METRIC")
    
    # Serverless Configuration
    cloud: str = Field("aws", env="PINECONE_CLOUD")
    region: str = Field("us-east-1", env="PINECONE_REGION")
    
    # Query Configuration
    top_k: int = Field(10, env="PINECONE_TOP_K")
    include_metadata: bool = Field(True, env="PINECONE_INCLUDE_METADATA")
    include_values: bool = Field(False, env="PINECONE_INCLUDE_VALUES")
    
    # Batch Configuration
    batch_size: int = Field(100, env="PINECONE_BATCH_SIZE")
    max_retries: int = Field(3, env="PINECONE_MAX_RETRIES")
    timeout: int = Field(30, env="PINECONE_TIMEOUT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @validator("metric")
    def validate_metric(cls, v):
        allowed_metrics = ["cosine", "euclidean", "dotproduct"]
        if v not in allowed_metrics:
            raise ValueError(f"Metric must be one of {allowed_metrics}")
        return v
    
    @validator("dimension")
    def validate_dimension(cls, v):
        if v <= 0 or v > 20000:
            raise ValueError("Dimension must be between 1 and 20000")
        return v


class PineconeManager:
    """Pinecone vector database manager"""
    
    def __init__(self, settings: Optional[PineconeSettings] = None):
        self.settings = settings or PineconeSettings()
        self.client: Optional[Pinecone] = None
        self.index = None
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize Pinecone client and index"""
        try:
            # Check if API key is available
            if not self.settings.api_key:
                logger.warning("Pinecone API key not provided. Pinecone functionality will be disabled.")
                return False
            
            # Initialize Pinecone client
            self.client = Pinecone(api_key=self.settings.api_key)
            
            # Check if index exists, create if not
            if not await self._index_exists():
                await self._create_index()
            
            # Get index reference
            self.index = self.client.Index(self.settings.index_name)
            self._initialized = True
            
            logger.info(f"Pinecone initialized successfully with index: {self.settings.index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {str(e)}")
            return False
    
    async def _index_exists(self) -> bool:
        """Check if index exists"""
        try:
            indexes = self.client.list_indexes()
            return any(idx.name == self.settings.index_name for idx in indexes)
        except Exception as e:
            logger.error(f"Error checking index existence: {str(e)}")
            return False
    
    async def _create_index(self):
        """Create new Pinecone index"""
        try:
            self.client.create_index(
                name=self.settings.index_name,
                dimension=self.settings.dimension,
                metric=self.settings.metric,
                spec=ServerlessSpec(
                    cloud=self.settings.cloud,
                    region=self.settings.region
                )
            )
            logger.info(f"Created Pinecone index: {self.settings.index_name}")
            
        except Exception as e:
            logger.error(f"Failed to create index: {str(e)}")
            raise
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        if not self._check_initialized():
            return {}
        
        try:
            stats = self.index.describe_index_stats()
            return {
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "total_vector_count": stats.total_vector_count,
                "namespaces": dict(stats.namespaces) if stats.namespaces else {}
            }
        except Exception as e:
            logger.error(f"Error getting index stats: {str(e)}")
            return {}
    
    async def upsert_vectors(
        self, 
        vectors: List[Dict[str, Any]], 
        namespace: str = ""
    ) -> bool:
        """Upsert vectors to index"""
        if not self._check_initialized():
            return False
        
        try:
            # Process in batches
            for i in range(0, len(vectors), self.settings.batch_size):
                batch = vectors[i:i + self.settings.batch_size]
                self.index.upsert(vectors=batch, namespace=namespace)
            
            logger.info(f"Upserted {len(vectors)} vectors to namespace: {namespace}")
            return True
            
        except Exception as e:
            logger.error(f"Error upserting vectors: {str(e)}")
            return False
    
    async def query_vectors(
        self,
        query_vector: List[float],
        namespace: str = "",
        filter_dict: Optional[Dict[str, Any]] = None,
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query similar vectors"""
        if not self._check_initialized():
            return []
        
        try:
            response = self.index.query(
                vector=query_vector,
                top_k=top_k or self.settings.top_k,
                include_metadata=self.settings.include_metadata,
                include_values=self.settings.include_values,
                namespace=namespace,
                filter=filter_dict
            )
            
            return [
                {
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata if match.metadata else {},
                    "values": match.values if match.values else []
                }
                for match in response.matches
            ]
            
        except Exception as e:
            logger.error(f"Error querying vectors: {str(e)}")
            return []
    
    async def delete_vectors(
        self, 
        ids: List[str], 
        namespace: str = ""
    ) -> bool:
        """Delete vectors by IDs"""
        if not self._check_initialized():
            return False
        
        try:
            self.index.delete(ids=ids, namespace=namespace)
            logger.info(f"Deleted {len(ids)} vectors from namespace: {namespace}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting vectors: {str(e)}")
            return False
    
    async def delete_namespace(self, namespace: str) -> bool:
        """Delete entire namespace"""
        if not self._check_initialized():
            return False
        
        try:
            self.index.delete(delete_all=True, namespace=namespace)
            logger.info(f"Deleted namespace: {namespace}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting namespace: {str(e)}")
            return False
    
    def _check_initialized(self) -> bool:
        """Check if manager is initialized"""
        if not self._initialized:
            logger.error("PineconeManager not initialized. Call initialize() first.")
            return False
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            if not self.settings.api_key:
                return {
                    "status": "warning", 
                    "message": "Pinecone API key not configured",
                    "configured": False
                }
            
            if not self._initialized:
                return {"status": "error", "message": "Not initialized"}
            
            stats = await self.get_index_stats()
            return {
                "status": "healthy",
                "index_name": self.settings.index_name,
                "dimension": self.settings.dimension,
                "total_vectors": stats.get("total_vector_count", 0),
                "index_fullness": stats.get("index_fullness", 0),
                "configured": True
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "configured": bool(self.settings.api_key)
            }


# Global instance - will be initialized lazily
pinecone_manager = None


async def get_pinecone_manager() -> PineconeManager:
    """Dependency injection for Pinecone manager"""
    global pinecone_manager
    
    if pinecone_manager is None:
        pinecone_manager = PineconeManager()
        # Try to initialize, but don't fail if API key is missing
        await pinecone_manager.initialize()
    
    return pinecone_manager
