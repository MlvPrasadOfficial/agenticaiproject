"""
Pydantic models for RAG (Retrieval-Augmented Generation) system

These models define the data structures for:
- Vector embeddings
- Document chunks
- Search requests and responses
- Vector storage operations
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# Constants for commonly used field descriptions
OPTIONAL_FILE_ID_DESC = "Optional file ID to filter results"
ORIGINAL_SEARCH_QUERY_DESC = "Original search query"
TOP_K_DESC = "Number of top results to return"

class EmbeddingRequest(BaseModel):
    """Request model for generating embeddings"""
    texts: List[str] = Field(..., description="List of texts to generate embeddings for")
    model_name: Optional[str] = Field(default="all-MiniLM-L6-v2", description="Embedding model to use")

class EmbeddingResponse(BaseModel):
    """Response model for generated embeddings"""
    embeddings: List[List[float]] = Field(..., description="Generated embedding vectors")
    model_name: str = Field(..., description="Model used for embeddings")
    dimension: int = Field(..., description="Dimension of embedding vectors")
    count: int = Field(..., description="Number of embeddings generated")

class DocumentChunk(BaseModel):
    """Model for document chunks"""
    id: str = Field(..., description="Unique identifier for the chunk")
    text: str = Field(..., description="Text content of the chunk")
    start_pos: int = Field(..., description="Starting character position in original document")
    end_pos: int = Field(..., description="Ending character position in original document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the chunk")

class ChunkingRequest(BaseModel):
    """Request model for document chunking"""
    text: str = Field(..., description="Document text to chunk")
    chunk_size: int = Field(default=1000, description="Maximum size of each chunk in characters")
    overlap: int = Field(default=200, description="Number of characters to overlap between chunks")
    file_id: Optional[str] = Field(default=None, description="File ID for reference")

class ChunkingResponse(BaseModel):
    """Response model for document chunking"""
    chunks: List[DocumentChunk] = Field(..., description="Generated document chunks")
    total_chunks: int = Field(..., description="Total number of chunks created")
    original_length: int = Field(..., description="Length of original document in characters")
    average_chunk_size: float = Field(..., description="Average chunk size in characters")

class VectorStoreRequest(BaseModel):
    """Request model for storing vectors"""
    file_id: str = Field(..., description="Unique identifier for the source file")
    chunks: List[DocumentChunk] = Field(..., description="Document chunks to store as vectors")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata to store")

class VectorStoreResponse(BaseModel):
    """Response model for vector storage"""
    file_id: str = Field(..., description="File ID that was processed")
    chunks_stored: int = Field(..., description="Number of chunks that were stored")
    vectors_created: int = Field(..., description="Number of vectors created in the database")
    index_name: str = Field(..., description="Name of the vector index used")
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Status message")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of storage")

class SearchRequest(BaseModel):
    """Request model for vector search"""
    query: str = Field(..., description="Search query text")
    top_k: int = Field(default=10, description=TOP_K_DESC)
    file_id: Optional[str] = Field(default=None, description=OPTIONAL_FILE_ID_DESC)
    search_type: str = Field(default="semantic", description="Type of search: semantic, hybrid, or keyword")
    threshold: Optional[float] = Field(default=None, description="Minimum similarity threshold")

class SearchResult(BaseModel):
    """Model for individual search result"""
    id: str = Field(..., description="Unique identifier of the result")
    score: float = Field(..., description="Similarity score (0-1)")
    text: str = Field(..., description="Text content of the result")
    file_id: str = Field(..., description="Source file ID")
    chunk_id: str = Field(..., description="Chunk ID within the file")
    start_pos: int = Field(..., description="Starting position in original document")
    end_pos: int = Field(..., description="Ending position in original document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class SearchResponse(BaseModel):
    """Response model for search operations"""
    query: str = Field(..., description="Original search query")
    results: List[SearchResult] = Field(..., description="List of search results")
    total_results: int = Field(..., description="Total number of results found")
    search_type: str = Field(..., description="Type of search performed")
    execution_time: Optional[float] = Field(default=None, description="Search execution time in seconds")
    success: bool = Field(default=True, description="Whether the search was successful")
    error: Optional[str] = Field(default=None, description="Error message if search failed")

class HybridSearchRequest(BaseModel):
    """Request model for hybrid search combining vector and keyword search"""
    query: str = Field(..., description="Search query text")
    top_k: int = Field(default=10, description="Number of top results to return")
    alpha: float = Field(default=0.7, description="Weight for vector search (0-1), 1-alpha for keyword")
    file_id: Optional[str] = Field(default=None, description="Optional file ID to filter results")
    keywords: Optional[List[str]] = Field(default=None, description="Additional keywords for search")

class ContextRetrievalRequest(BaseModel):
    """Request model for context retrieval with ranking"""
    query: str = Field(..., description="Query for context retrieval")
    top_k: int = Field(default=10, description="Number of contexts to retrieve")
    context_window: int = Field(default=3, description="Number of surrounding chunks to include")
    file_id: Optional[str] = Field(default=None, description="Optional file ID to filter results")

class QueryExpansionRequest(BaseModel):
    """Request model for query expansion"""
    query: str = Field(..., description="Original query to expand")
    method: str = Field(default="similarity", description="Expansion method: similarity, wordnet, or llm")
    num_expansions: int = Field(default=5, description="Number of expansion terms to add")

class RerankingRequest(BaseModel):
    """Request model for cross-encoder reranking"""
    query: str = Field(..., description="Original search query")
    results: List[Dict[str, Any]] = Field(..., description="Search results to rerank")
    top_k: int = Field(default=10, description="Number of top results after reranking")

class RAGStatsResponse(BaseModel):
    """Response model for RAG system statistics"""
    total_vectors: int = Field(..., description="Total number of vectors stored")
    total_files: int = Field(..., description="Total number of files processed")
    index_name: str = Field(..., description="Name of the vector index")
    embedding_model: str = Field(..., description="Current embedding model")
    embedding_dimension: int = Field(..., description="Dimension of embeddings")
    index_size_bytes: Optional[int] = Field(default=None, description="Size of index in bytes")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update time")
    health_status: str = Field(..., description="Overall health status")

class RAGHealthResponse(BaseModel):
    """Response model for RAG health check"""
    status: str = Field(..., description="Overall health status: healthy, degraded, or unhealthy")
    embedding_model_ready: bool = Field(..., description="Whether embedding model is loaded")
    vector_store_ready: bool = Field(..., description="Whether vector store is accessible")
    model_name: str = Field(..., description="Name of the embedding model")
    embedding_dimension: int = Field(..., description="Dimension of embeddings")
    index_name: str = Field(..., description="Name of the vector index")
    stats: Dict[str, Any] = Field(default_factory=dict, description="Additional statistics")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")

class RAGStats(BaseModel):
    """Model for RAG system statistics"""
    total_documents: int = Field(..., description="Total number of documents in the system")
    total_chunks: int = Field(..., description="Total number of chunks stored")
    total_vectors: int = Field(..., description="Total number of vectors in the database")
    index_size_mb: float = Field(..., description="Size of the vector index in MB")
    last_updated: datetime = Field(..., description="Last update timestamp")
    embedding_model: str = Field(..., description="Current embedding model in use")
    vector_dimension: int = Field(..., description="Dimension of vectors in the system")

class RAGHealthCheck(BaseModel):
    """Model for RAG system health check"""
    embedding_service: bool = Field(..., description="Whether embedding service is healthy")
    vector_database: bool = Field(..., description="Whether vector database is accessible")
    index_status: str = Field(..., description="Status of the vector index")
    model_loaded: bool = Field(..., description="Whether embedding model is loaded")
    last_check: datetime = Field(default_factory=datetime.utcnow, description="Last health check timestamp")
    overall_health: bool = Field(..., description="Overall system health status")

class DiversityEnforcementRequest(BaseModel):
    """Request model for enforcing diversity in search results"""
    results: List[SearchResult] = Field(..., description="Search results to diversify")
    diversity_threshold: float = Field(default=0.7, description="Minimum diversity score (0-1)")
    max_results: int = Field(default=10, description="Maximum number of diverse results")

class AdvancedSearchRequest(BaseModel):
    """Request model for advanced search with multiple parameters"""
    query: str = Field(..., description="Main search query")
    search_types: List[str] = Field(default=["semantic"], description="Types of search to perform")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Filters to apply")
    ranking_weights: Dict[str, float] = Field(default_factory=dict, description="Weights for different ranking factors")
    post_processing: List[str] = Field(default_factory=list, description="Post-processing steps to apply")
    top_k: int = Field(default=10, description="Number of results to return")

class AdvancedSearchResponse(BaseModel):
    """Response model for advanced search"""
    query: str = Field(..., description="Original search query")
    results: List[SearchResult] = Field(..., description="Final search results")
    search_metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata about search execution")
    execution_time: float = Field(..., description="Total execution time in seconds")
    result_sources: Dict[str, int] = Field(default_factory=dict, description="Count of results from each source")
    success: bool = Field(default=True, description="Whether search was successful")
    warnings: List[str] = Field(default_factory=list, description="Any warnings during search")
