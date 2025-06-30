"""
RAG (Retrieval-Augmented Generation) API Endpoints

This module provides comprehensive REST API endpoints for the RAG system including:
- Vector embedding generation
- Document chunking and storage
- Semantic and hybrid search
- Context retrieval and ranking
- Query expansion and reranking
- Diversity enforcement
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.responses import JSONResponse

from app.services.rag_service import get_rag_service, RAGService
from app.models.rag_models import (
    EmbeddingRequest,
    EmbeddingResponse,
    DocumentChunk,
    SearchRequest,
    SearchResponse,
    VectorStoreRequest,
    VectorStoreResponse,
    HybridSearchRequest,
    ContextRetrievalRequest,
    QueryExpansionRequest,
    RerankingRequest,
    RAGStatsResponse,
    RAGHealthResponse,
    ChunkingRequest,
    ChunkingResponse
)
from app.core.pinecone_config import get_pinecone_manager, PineconeManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["RAG System"])

# Health and Status Endpoints
@router.get("/health", response_model=RAGHealthResponse)
async def get_rag_health(
    rag_service: RAGService = Depends(get_rag_service)
) -> RAGHealthResponse:
    """Get comprehensive RAG system health status"""
    try:
        # Check if models and services are initialized
        embedding_model_ready = rag_service.embedding_model is not None
        pinecone_ready = rag_service.index is not None
        
        # Get basic stats if available
        stats = {}
        if pinecone_ready:
            try:
                index_stats = rag_service.index.describe_index_stats()
                stats = {
                    "total_vectors": index_stats.get("total_vector_count", 0),
                    "index_name": rag_service.index_name,
                    "namespaces": len(index_stats.get("namespaces", {}))
                }
            except Exception as e:
                logger.warning(f"Could not get index stats: {e}")
        
        health_status = "healthy" if (embedding_model_ready and pinecone_ready) else "unhealthy"
        
        return RAGHealthResponse(
            status=health_status,
            embedding_model_ready=embedding_model_ready,
            vector_store_ready=pinecone_ready,
            model_name=rag_service.model_name,
            embedding_dimension=rag_service.embedding_dimension,
            index_name=rag_service.index_name,
            stats=stats
        )
        
    except Exception as e:
        logger.error(f"RAG health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG health check failed: {str(e)}"
        )

@router.get("/stats", response_model=Dict[str, Any])
async def get_rag_stats(
    rag_service: RAGService = Depends(get_rag_service)
) -> Dict[str, Any]:
    """Get comprehensive RAG system statistics and metrics"""
    try:
        stats = await rag_service.get_stats()
        return {
            "status": "success",
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"RAG stats retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG stats retrieval failed: {str(e)}"
        )

# Core RAG Functionality
@router.post("/embeddings", response_model=EmbeddingResponse)
async def generate_embeddings(
    request: EmbeddingRequest,
    rag_service: RAGService = Depends(get_rag_service)
) -> EmbeddingResponse:
    """Generate vector embeddings for text inputs"""
    try:
        logger.info(f"Generating embeddings for {len(request.texts)} texts")
        
        embeddings = await rag_service.generate_embeddings(request.texts)
        
        return EmbeddingResponse(
            embeddings=embeddings,
            model_name=rag_service.model_name,
            dimension=rag_service.embedding_dimension,
            count=len(request.texts)
        )
        
    except Exception as e:
        logger.error(f"Embedding generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Embedding generation failed: {str(e)}"
        )

@router.post("/document/chunk")
async def chunk_document(
    file: UploadFile = File(...),
    chunk_size: int = 1000,
    overlap: int = 200,
    rag_service: RAGService = Depends(get_rag_service)
) -> JSONResponse:
    """Chunk a document into smaller pieces for embedding"""
    try:
        logger.info(f"Chunking document: {file.filename}")
        
        # Read file content
        content = await file.read()
        text = content.decode('utf-8')
        
        # Chunk the document
        chunks = rag_service.chunk_document(text, chunk_size, overlap)
        
        # Convert chunks to dictionary format
        chunks_data = [
            {
                "id": chunk.id,
                "text": chunk.text,
                "start_pos": chunk.start_pos,
                "end_pos": chunk.end_pos,
                "metadata": chunk.metadata
            }
            for chunk in chunks
        ]
        
        return JSONResponse(content={
            "filename": file.filename,
            "total_chunks": len(chunks),
            "chunks": chunks_data,
            "chunk_size": chunk_size,
            "overlap": overlap,
            "original_length": len(text),
            "average_chunk_size": sum(len(chunk.text) for chunk in chunks) / len(chunks) if chunks else 0
        })
        
    except Exception as e:
        logger.error(f"Document chunking failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document chunking failed: {str(e)}"
        )

@router.post("/store", response_model=VectorStoreResponse)
async def store_document_vectors(
    request: VectorStoreRequest,
    rag_service: RAGService = Depends(get_rag_service)
) -> VectorStoreResponse:
    """Store document chunks as vectors in the vector database"""
    try:
        logger.info(f"Storing vectors for file: {request.file_id}")
        
        # Convert request chunks to DocumentChunk objects
        chunks = [
            DocumentChunk(
                id=chunk_data["id"],
                text=chunk_data["text"],
                start_pos=chunk_data["start_pos"],
                end_pos=chunk_data["end_pos"],
                metadata=chunk_data.get("metadata", {})
            )
            for chunk_data in request.chunks
        ]
        
        # Store vectors
        response = await rag_service.store_vectors(
            chunks=chunks,
            file_id=request.file_id,
            metadata=request.metadata
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Vector storage failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vector storage failed: {str(e)}"
        )

# Search Endpoints
@router.post("/search", response_model=SearchResponse)
async def semantic_search(
    request: SearchRequest,
    rag_service: RAGService = Depends(get_rag_service)
) -> SearchResponse:
    """Perform semantic search using vector similarity"""
    try:
        logger.info(f"Semantic search for: {request.query[:100]}...")
        
        response = await rag_service.semantic_search(
            query=request.query,
            top_k=request.top_k,
            file_id=request.file_id
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Semantic search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Semantic search failed: {str(e)}"
        )

@router.post("/search/hybrid", response_model=SearchResponse)
async def hybrid_search(
    request: HybridSearchRequest,
    rag_service: RAGService = Depends(get_rag_service)
) -> SearchResponse:
    """Perform hybrid search combining vector and keyword search"""
    try:
        logger.info(f"Hybrid search for: {request.query[:100]}...")
        
        response = await rag_service.hybrid_search(
            query=request.query,
            top_k=request.top_k,
            alpha=request.alpha,
            file_id=request.file_id,
            keywords=request.keywords
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Hybrid search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hybrid search failed: {str(e)}"
        )

# Advanced RAG Features
@router.post("/context/retrieve")
async def retrieve_context(
    request: ContextRetrievalRequest,
    rag_service: RAGService = Depends(get_rag_service)
) -> JSONResponse:
    """Retrieve and rank context for a given query with surrounding chunks"""
    try:
        logger.info(f"Context retrieval for: {request.query[:100]}...")
        
        response = await rag_service.retrieve_context(
            query=request.query,
            top_k=request.top_k,
            context_window=request.context_window,
            file_id=request.file_id
        )
        
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"Context retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Context retrieval failed: {str(e)}"
        )

@router.post("/query/expand")
async def expand_query(
    request: QueryExpansionRequest,
    rag_service: RAGService = Depends(get_rag_service)
) -> JSONResponse:
    """Expand query for better retrieval using synonyms and related terms"""
    try:
        logger.info(f"Query expansion for: {request.query[:100]}...")
        
        response = await rag_service.expand_query(
            query=request.query,
            method=request.method,
            num_expansions=request.num_expansions
        )
        
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"Query expansion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query expansion failed: {str(e)}"
        )

@router.post("/rerank")
async def rerank_results(
    request: RerankingRequest,
    rag_service: RAGService = Depends(get_rag_service)
) -> JSONResponse:
    """Rerank search results using cross-encoder for better relevance"""
    try:
        logger.info(f"Reranking {len(request.results)} results for: {request.query[:100]}...")
        
        response = await rag_service.rerank_results(
            query=request.query,
            results=request.results,
            top_k=request.top_k
        )
        
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"Result reranking failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Result reranking failed: {str(e)}"
        )

@router.post("/diversity/enforce")
async def enforce_diversity(
    results: List[Dict[str, Any]],
    diversity_threshold: float = 0.7,
    max_results: int = 10,
    rag_service: RAGService = Depends(get_rag_service)
) -> JSONResponse:
    """Enforce diversity in search results to avoid redundant information"""
    try:
        logger.info(f"Enforcing diversity on {len(results)} results")
        
        diverse_results = await rag_service.enforce_diversity(
            results=results,
            diversity_threshold=diversity_threshold,
            max_results=max_results
        )
        
        return JSONResponse(content={
            "original_count": len(results),
            "diverse_count": len(diverse_results),
            "diversity_threshold": diversity_threshold,
            "diverse_results": diverse_results,
            "success": True
        })
        
    except Exception as e:
        logger.error(f"Diversity enforcement failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Diversity enforcement failed: {str(e)}"
        )

# Management Endpoints
@router.delete("/vectors/{file_id}")
async def delete_file_vectors(
    file_id: str,
    rag_service: RAGService = Depends(get_rag_service)
) -> JSONResponse:
    """Delete all vectors for a specific file"""
    try:
        logger.info(f"Deleting vectors for file: {file_id}")
        
        result = await rag_service.delete_file_vectors(file_id)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Vector deletion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vector deletion failed: {str(e)}"
        )

# Legacy Pinecone Management Endpoints (maintained for backward compatibility)
@router.post("/initialize")
async def initialize_pinecone(
    pinecone: PineconeManager = Depends(get_pinecone_manager)
) -> Dict[str, Any]:
    """Initialize or reinitialize Pinecone connection"""
    try:
        success = await pinecone.initialize()
        if success:
            return {
                "status": "success",
                "message": "Pinecone initialized successfully",
                "index_name": pinecone.settings.index_name
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to initialize Pinecone")
    except Exception as e:
        logger.error(f"Pinecone initialization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")

@router.delete("/namespace/{namespace}")
async def delete_namespace(
    namespace: str,
    pinecone: PineconeManager = Depends(get_pinecone_manager)
) -> Dict[str, Any]:
    """Delete a specific namespace from the index"""
    try:
        success = await pinecone.delete_namespace(namespace)
        if success:
            return {
                "status": "success",
                "message": f"Namespace '{namespace}' deleted successfully"
            }
        else:
            raise HTTPException(status_code=500, detail=f"Failed to delete namespace '{namespace}'")
    except Exception as e:
        logger.error(f"Failed to delete namespace {namespace}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Delete operation failed: {str(e)}")

@router.get("/namespaces")
async def list_namespaces(
    pinecone: PineconeManager = Depends(get_pinecone_manager)
) -> Dict[str, Any]:
    """List all namespaces in the index"""
    try:
        stats = await pinecone.get_index_stats()
        namespaces = stats.get("namespaces", {})
        return {
            "status": "success",
            "namespaces": namespaces,
            "total_namespaces": len(namespaces)
        }
    except Exception as e:
        logger.error(f"Failed to list namespaces: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list namespaces: {str(e)}")
