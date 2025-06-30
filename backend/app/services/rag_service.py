"""
RAG (Retrieval-Augmented Generation) Service

This service handles vector embeddings, document processing, and semantic search
for the Enterprise Insights Copilot RAG system.

Components:
1. Vector embedding generation with sentence-transformers
2. Document chunking and preprocessing
3. Vector storage and retrieval with Pinecone
4. Semantic search functionality
5. Hybrid search (vector + keyword)
6. Context retrieval with ranking
7. Query expansion and reranking
"""

import logging
import os
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import hashlib

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import pinecone
from pinecone import Pinecone, ServerlessSpec

from app.core.config import settings
from app.models.rag_models import (
    EmbeddingRequest,
    EmbeddingResponse,
    DocumentChunk,
    SearchRequest,
    SearchResponse,
    VectorStoreRequest,
    VectorStoreResponse
)

logger = logging.getLogger(__name__)

class RAGService:
    """
    RAG Service for vector embeddings and semantic search
    
    This service provides comprehensive RAG functionality including:
    - Vector embedding generation using sentence-transformers
    - Document chunking and preprocessing
    - Vector storage and retrieval with Pinecone
    - Semantic and hybrid search capabilities
    """
    
    def __init__(self):
        self.embedding_model = None
        self.pinecone_client = None
        self.index = None
        self.model_name = "all-MiniLM-L6-v2"  # Fast, efficient model for embeddings
        self.embedding_dimension = 384  # Dimension for all-MiniLM-L6-v2
        self.index_name = "enterprise-insights"
        
    async def initialize(self):
        """Initialize the RAG service with embedding model and Pinecone"""
        try:
            logger.info("Initializing RAG Service...")
            
            # Initialize sentence-transformers model
            logger.info(f"Loading embedding model: {self.model_name}")
            self.embedding_model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")
            
            # Initialize Pinecone
            await self._initialize_pinecone()
            
            logger.info("RAG Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG Service: {str(e)}")
            raise
    
    async def _initialize_pinecone(self):
        """Initialize Pinecone client and index"""
        try:
            logger.info("Initializing Pinecone...")
            
            # Initialize Pinecone client
            self.pinecone_client = Pinecone(
                api_key=settings.PINECONE_API_KEY
            )
            
            # Check if index exists, create if not
            existing_indexes = self.pinecone_client.list_indexes()
            index_names = [index.name for index in existing_indexes]
            
            if self.index_name not in index_names:
                logger.info(f"Creating Pinecone index: {self.index_name}")
                self.pinecone_client.create_index(
                    name=self.index_name,
                    dimension=self.embedding_dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                logger.info("Index created successfully")
            else:
                logger.info(f"Index {self.index_name} already exists")
            
            # Connect to index
            self.index = self.pinecone_client.Index(self.index_name)
            logger.info("Connected to Pinecone index successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {str(e)}")
            raise
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate vector embeddings for a list of texts
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (each vector is a list of floats)
        """
        try:
            logger.info(f"Generating embeddings for {len(texts)} texts")
            
            if not self.embedding_model:
                await self.initialize()
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=True if len(texts) > 10 else False
            )
            
            # Convert numpy arrays to lists for JSON serialization
            embeddings_list = [embedding.tolist() for embedding in embeddings]
            
            logger.info(f"Generated {len(embeddings_list)} embeddings successfully")
            return embeddings_list
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {str(e)}")
            raise
    
    def chunk_document(
        self, 
        text: str, 
        chunk_size: int = 1000, 
        overlap: int = 200
    ) -> List[DocumentChunk]:
        """
        Chunk a document into smaller pieces for embedding
        
        Args:
            text: The document text to chunk
            chunk_size: Maximum size of each chunk in characters
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of DocumentChunk objects
        """
        try:
            logger.info(f"Chunking document of length {len(text)} characters")
            
            chunks = []
            start = 0
            chunk_id = 0
            
            while start < len(text):
                end = min(start + chunk_size, len(text))
                
                # Try to break at sentence boundaries
                if end < len(text):
                    # Look for sentence ending within the last 100 characters
                    sentence_end = text.rfind('.', start, end)
                    if sentence_end > start + chunk_size - 100:
                        end = sentence_end + 1
                
                chunk_text = text[start:end].strip()
                
                if chunk_text:  # Only add non-empty chunks
                    chunk = DocumentChunk(
                        id=f"chunk_{chunk_id}",
                        text=chunk_text,
                        start_pos=start,
                        end_pos=end,
                        metadata={
                            "chunk_index": chunk_id,
                            "character_count": len(chunk_text),
                            "word_count": len(chunk_text.split())
                        }
                    )
                    chunks.append(chunk)
                    chunk_id += 1
                
                # Move start position with overlap
                start = end - overlap if end < len(text) else len(text)
            
            logger.info(f"Created {len(chunks)} chunks from document")
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to chunk document: {str(e)}")
            raise
    
    async def store_vectors(
        self, 
        chunks: List[DocumentChunk], 
        file_id: str,
        metadata: Dict[str, Any] = None
    ) -> VectorStoreResponse:
        """
        Store document chunks as vectors in Pinecone
        
        Args:
            chunks: List of document chunks to store
            file_id: Unique identifier for the source file
            metadata: Additional metadata to store with vectors
            
        Returns:
            VectorStoreResponse with storage details
        """
        try:
            logger.info(f"Storing {len(chunks)} chunks as vectors for file {file_id}")
            
            if not self.index:
                await self.initialize()
            
            # Generate embeddings for all chunks
            texts = [chunk.text for chunk in chunks]
            embeddings = await self.generate_embeddings(texts)
            
            # Prepare vectors for Pinecone
            vectors_to_upsert = []
            
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                vector_id = f"{file_id}_{chunk.id}"
                
                # Prepare metadata
                vector_metadata = {
                    "file_id": file_id,
                    "chunk_id": chunk.id,
                    "text": chunk.text[:1000],  # Limit text length for metadata
                    "start_pos": chunk.start_pos,
                    "end_pos": chunk.end_pos,
                    "chunk_index": chunk.metadata.get("chunk_index", i),
                    "character_count": chunk.metadata.get("character_count", len(chunk.text)),
                    "word_count": chunk.metadata.get("word_count", len(chunk.text.split())),
                    "created_at": datetime.utcnow().isoformat(),
                }
                
                # Add additional metadata if provided
                if metadata:
                    vector_metadata.update(metadata)
                
                vectors_to_upsert.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": vector_metadata
                })
            
            # Upsert vectors to Pinecone (batch operation)
            batch_size = 100  # Pinecone batch limit
            total_upserted = 0
            
            for i in range(0, len(vectors_to_upsert), batch_size):
                batch = vectors_to_upsert[i:i + batch_size]
                self.index.upsert(vectors=batch)
                total_upserted += len(batch)
                logger.info(f"Upserted batch {i//batch_size + 1}, total: {total_upserted}")
            
            logger.info(f"Successfully stored {total_upserted} vectors for file {file_id}")
            
            return VectorStoreResponse(
                file_id=file_id,
                chunks_stored=len(chunks),
                vectors_created=total_upserted,
                index_name=self.index_name,
                success=True,
                message=f"Successfully stored {total_upserted} vectors"
            )
            
        except Exception as e:
            logger.error(f"Failed to store vectors: {str(e)}")
            return VectorStoreResponse(
                file_id=file_id,
                chunks_stored=0,
                vectors_created=0,
                index_name=self.index_name,
                success=False,
                message=f"Failed to store vectors: {str(e)}"
            )
    
    async def semantic_search(
        self, 
        query: str, 
        top_k: int = 10,
        file_id: Optional[str] = None
    ) -> SearchResponse:
        """
        Perform semantic search using vector similarity
        
        Args:
            query: Search query text
            top_k: Number of top results to return
            file_id: Optional file ID to filter results
            
        Returns:
            SearchResponse with ranked results
        """
        try:
            logger.info(f"Performing semantic search for query: '{query[:100]}...'")
            
            if not self.index:
                await self.initialize()
            
            # Generate embedding for query
            query_embedding = await self.generate_embeddings([query])
            
            # Prepare filter if file_id is provided
            filter_dict = {"file_id": file_id} if file_id else None
            
            # Search in Pinecone
            search_results = self.index.query(
                vector=query_embedding[0],
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
            
            # Process results
            results = []
            for match in search_results.matches:
                result = {
                    "id": match.id,
                    "score": float(match.score),
                    "text": match.metadata.get("text", ""),
                    "file_id": match.metadata.get("file_id", ""),
                    "chunk_id": match.metadata.get("chunk_id", ""),
                    "start_pos": match.metadata.get("start_pos", 0),
                    "end_pos": match.metadata.get("end_pos", 0),
                    "metadata": match.metadata
                }
                results.append(result)
            
            logger.info(f"Found {len(results)} semantic search results")
            
            return SearchResponse(
                query=query,
                results=results,
                total_results=len(results),
                search_type="semantic",
                success=True
            )
            
        except Exception as e:
            logger.error(f"Semantic search failed: {str(e)}")
            return SearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_type="semantic",
                success=False,
                error=str(e)
            )

    async def hybrid_search(
        self, 
        query: str, 
        top_k: int = 10,
        alpha: float = 0.7,
        file_id: Optional[str] = None,
        keywords: Optional[List[str]] = None
    ) -> SearchResponse:
        """
        Perform hybrid search combining vector similarity and keyword matching
        
        Args:
            query: Search query text
            top_k: Number of top results to return
            alpha: Weight for vector search (0-1), 1-alpha for keyword search
            file_id: Optional file ID to filter results
            keywords: Additional keywords for search
            
        Returns:
            SearchResponse with ranked hybrid results
        """
        try:
            logger.info(f"Performing hybrid search for query: '{query[:100]}...'")
            
            # Perform semantic search
            semantic_results = await self.semantic_search(query, top_k * 2, file_id)
            
            # Perform keyword search (simple implementation)
            keyword_results = await self._keyword_search(query, top_k * 2, file_id, keywords)
            
            # Combine and rerank results
            combined_results = self._combine_search_results(
                semantic_results.results, 
                keyword_results, 
                alpha, 
                top_k
            )
            
            logger.info(f"Found {len(combined_results)} hybrid search results")
            
            return SearchResponse(
                query=query,
                results=combined_results,
                total_results=len(combined_results),
                search_type="hybrid",
                success=True
            )
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {str(e)}")
            return SearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_type="hybrid",
                success=False,
                error=str(e)
            )
    
    async def _keyword_search(
        self, 
        query: str, 
        top_k: int, 
        file_id: Optional[str] = None,
        additional_keywords: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform keyword-based search using metadata filtering
        """
        try:
            # Extract keywords from query
            keywords = query.lower().split()
            if additional_keywords:
                keywords.extend([kw.lower() for kw in additional_keywords])
            
            # Search using metadata filtering (simplified implementation)
            # In a production system, you might use Elasticsearch or similar
            
            # For now, we'll do a text-based search through stored metadata
            filter_dict = {}
            if file_id:
                filter_dict["file_id"] = file_id
            
            # This is a simplified keyword search - in production you'd want
            # more sophisticated text matching
            search_results = self.index.query(
                vector=[0.0] * self.embedding_dimension,  # Dummy vector
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
            
            # Score results based on keyword matches
            keyword_scored_results = []
            for match in search_results.matches:
                text = match.metadata.get("text", "").lower()
                score = sum(1 for keyword in keywords if keyword in text) / len(keywords)
                
                if score > 0:  # Only include results with keyword matches
                    result = {
                        "id": match.id,
                        "score": score,
                        "text": match.metadata.get("text", ""),
                        "file_id": match.metadata.get("file_id", ""),
                        "chunk_id": match.metadata.get("chunk_id", ""),
                        "start_pos": match.metadata.get("start_pos", 0),
                        "end_pos": match.metadata.get("end_pos", 0),
                        "metadata": match.metadata
                    }
                    keyword_scored_results.append(result)
            
            # Sort by keyword score
            keyword_scored_results.sort(key=lambda x: x["score"], reverse=True)
            return keyword_scored_results[:top_k]
            
        except Exception as e:
            logger.error(f"Keyword search failed: {str(e)}")
            return []
    
    def _combine_search_results(
        self, 
        semantic_results: List[Dict[str, Any]], 
        keyword_results: List[Dict[str, Any]], 
        alpha: float, 
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Combine semantic and keyword search results with weighted scoring
        """
        try:
            # Create a dictionary to track combined scores
            combined_scores = {}
            
            # Add semantic scores
            for result in semantic_results:
                result_id = result["id"]
                combined_scores[result_id] = {
                    "semantic_score": result["score"],
                    "keyword_score": 0.0,
                    "result": result
                }
            
            # Add keyword scores
            for result in keyword_results:
                result_id = result["id"]
                if result_id in combined_scores:
                    combined_scores[result_id]["keyword_score"] = result["score"]
                else:
                    combined_scores[result_id] = {
                        "semantic_score": 0.0,
                        "keyword_score": result["score"],
                        "result": result
                    }
            
            # Calculate combined scores
            final_results = []
            for result_id, scores in combined_scores.items():
                combined_score = (alpha * scores["semantic_score"] + 
                                (1 - alpha) * scores["keyword_score"])
                
                result = scores["result"].copy()
                result["score"] = combined_score
                result["semantic_score"] = scores["semantic_score"]
                result["keyword_score"] = scores["keyword_score"]
                final_results.append(result)
            
            # Sort by combined score and return top_k
            final_results.sort(key=lambda x: x["score"], reverse=True)
            return final_results[:top_k]
            
        except Exception as e:
            logger.error(f"Failed to combine search results: {str(e)}")
            return semantic_results[:top_k]  # Fallback to semantic results
    
    async def retrieve_context(
        self, 
        query: str, 
        top_k: int = 10,
        context_window: int = 3,
        file_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve context with surrounding chunks for better understanding
        
        Args:
            query: Query for context retrieval
            top_k: Number of initial results to retrieve
            context_window: Number of surrounding chunks to include
            file_id: Optional file ID filter
            
        Returns:
            Dictionary with context-enriched results
        """
        try:
            logger.info(f"Retrieving context for query: '{query[:100]}...'")
            
            # Get initial search results
            search_response = await self.semantic_search(query, top_k, file_id)
            
            if not search_response.success or not search_response.results:
                return {
                    "query": query,
                    "contexts": [],
                    "success": False,
                    "message": "No initial results found"
                }
            
            # Enrich results with surrounding context
            enriched_contexts = []
            
            for result in search_response.results:
                context = await self._get_surrounding_context(
                    result, context_window, file_id
                )
                enriched_contexts.append(context)
            
            logger.info(f"Retrieved {len(enriched_contexts)} enriched contexts")
            
            return {
                "query": query,
                "contexts": enriched_contexts,
                "total_contexts": len(enriched_contexts),
                "context_window": context_window,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Context retrieval failed: {str(e)}")
            return {
                "query": query,
                "contexts": [],
                "success": False,
                "error": str(e)
            }
    
    async def _get_surrounding_context(
        self, 
        result: Dict[str, Any], 
        context_window: int,
        file_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get surrounding chunks for a given result to provide more context
        """
        try:
            file_id = result.get("file_id")
            chunk_index = result.get("metadata", {}).get("chunk_index", 0)
            
            # Query for surrounding chunks
            surrounding_chunks = []
            
            for offset in range(-context_window, context_window + 1):
                if offset == 0:
                    continue  # Skip the original chunk
                    
                target_index = chunk_index + offset
                if target_index < 0:
                    continue
                
                # Search for the specific chunk
                # Note: This is a simplified implementation
                # In production, you'd want more efficient chunk retrieval
                filter_dict = {
                    "file_id": file_id,
                    "chunk_index": target_index
                }
                
                chunk_results = self.index.query(
                    vector=[0.0] * self.embedding_dimension,
                    top_k=1,
                    include_metadata=True,
                    filter=filter_dict
                )
                
                if chunk_results.matches:
                    chunk = chunk_results.matches[0]
                    surrounding_chunks.append({
                        "text": chunk.metadata.get("text", ""),
                        "chunk_index": target_index,
                        "position": "before" if offset < 0 else "after"
                    })
            
            return {
                "main_result": result,
                "surrounding_chunks": surrounding_chunks,
                "context_window": context_window
            }
            
        except Exception as e:
            logger.error(f"Failed to get surrounding context: {str(e)}")
            return {
                "main_result": result,
                "surrounding_chunks": [],
                "context_window": context_window
            }
    
    async def expand_query(
        self, 
        query: str, 
        method: str = "similarity",
        num_expansions: int = 5
    ) -> Dict[str, Any]:
        """
        Expand query with related terms for better retrieval
        
        Args:
            query: Original query to expand
            method: Expansion method (similarity, wordnet, llm)
            num_expansions: Number of expansion terms to generate
            
        Returns:
            Dictionary with expanded query and terms
        """
        try:
            logger.info(f"Expanding query: '{query}' using method: {method}")
            
            if method == "similarity":
                expanded_terms = await self._expand_query_similarity(query, num_expansions)
            elif method == "wordnet":
                expanded_terms = await self._expand_query_wordnet(query, num_expansions)
            elif method == "llm":
                expanded_terms = await self._expand_query_llm(query, num_expansions)
            else:
                expanded_terms = []
            
            expanded_query = f"{query} {' '.join(expanded_terms)}"
            
            return {
                "original_query": query,
                "expanded_query": expanded_query,
                "expansion_terms": expanded_terms,
                "method": method,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Query expansion failed: {str(e)}")
            return {
                "original_query": query,
                "expanded_query": query,
                "expansion_terms": [],
                "method": method,
                "success": False,
                "error": str(e)
            }
    
    async def _expand_query_similarity(self, query: str, num_expansions: int) -> List[str]:
        """Expand query using semantic similarity"""
        try:
            # Get similar documents and extract common terms
            search_response = await self.semantic_search(query, num_expansions * 2)
            
            term_freq = {}
            query_words = set(query.lower().split())
            
            for result in search_response.results:
                text = result.get("text", "").lower()
                words = text.split()
                
                for word in words:
                    if (len(word) > 3 and 
                        word not in query_words and 
                        word.isalpha()):
                        term_freq[word] = term_freq.get(word, 0) + 1
            
            # Sort by frequency and return top terms
            sorted_terms = sorted(term_freq.items(), key=lambda x: x[1], reverse=True)
            return [term for term, freq in sorted_terms[:num_expansions]]
            
        except Exception as e:
            logger.error(f"Similarity-based query expansion failed: {str(e)}")
            return []
    
    async def _expand_query_wordnet(self, query: str, num_expansions: int) -> List[str]:
        """Expand query using WordNet synonyms"""
        try:
            # This would require NLTK WordNet
            # For now, return empty list as a placeholder
            logger.warning("WordNet expansion not implemented yet")
            return []
            
        except Exception as e:
            logger.error(f"WordNet query expansion failed: {str(e)}")
            return []
    
    async def _expand_query_llm(self, query: str, num_expansions: int) -> List[str]:
        """Expand query using LLM generation"""
        try:
            # This would integrate with an LLM for query expansion
            # For now, return empty list as a placeholder
            logger.warning("LLM expansion not implemented yet")
            return []
            
        except Exception as e:
            logger.error(f"LLM query expansion failed: {str(e)}")
            return []
    
    async def rerank_results(
        self, 
        query: str, 
        results: List[Dict[str, Any]], 
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        Rerank search results using cross-encoder for better relevance
        
        Args:
            query: Original search query
            results: Search results to rerank
            top_k: Number of top results after reranking
            
        Returns:
            Dictionary with reranked results
        """
        try:
            logger.info(f"Reranking {len(results)} results for query: '{query[:100]}...'")
            
            # For now, implement a simple reranking based on text similarity
            # In production, you'd use a cross-encoder model like ms-marco-cross-encoder
            
            reranked_results = []
            
            for result in results:
                # Calculate additional relevance score
                text = result.get("text", "")
                relevance_score = self._calculate_text_relevance(query, text)
                
                # Combine original score with relevance score
                combined_score = (result.get("score", 0) * 0.7 + relevance_score * 0.3)
                
                reranked_result = result.copy()
                reranked_result["rerank_score"] = relevance_score
                reranked_result["combined_score"] = combined_score
                reranked_results.append(reranked_result)
            
            # Sort by combined score
            reranked_results.sort(key=lambda x: x["combined_score"], reverse=True)
            final_results = reranked_results[:top_k]
            
            logger.info(f"Reranked to {len(final_results)} results")
            
            return {
                "query": query,
                "reranked_results": final_results,
                "original_count": len(results),
                "reranked_count": len(final_results),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Result reranking failed: {str(e)}")
            return {
                "query": query,
                "reranked_results": results[:top_k],
                "original_count": len(results),
                "reranked_count": len(results[:top_k]),
                "success": False,
                "error": str(e)
            }
    
    def _calculate_text_relevance(self, query: str, text: str) -> float:
        """
        Calculate text relevance score based on term overlap and position
        """
        try:
            query_terms = set(query.lower().split())
            text_terms = text.lower().split()
            
            # Calculate term overlap
            overlap = len(query_terms.intersection(set(text_terms)))
            overlap_score = overlap / len(query_terms) if query_terms else 0
            
            # Calculate position score (earlier terms get higher score)
            position_score = 0
            for i, term in enumerate(text_terms[:50]):  # Only check first 50 terms
                if term in query_terms:
                    position_score += (50 - i) / 50
            
            position_score = position_score / len(query_terms) if query_terms else 0
            
            # Combine scores
            final_score = (overlap_score * 0.6 + position_score * 0.4)
            return min(final_score, 1.0)
            
        except Exception as e:
            logger.error(f"Text relevance calculation failed: {str(e)}")
            return 0.0
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive RAG system statistics
        """
        try:
            logger.info("Retrieving RAG system statistics")
            
            if not self.index:
                await self.initialize()
            
            # Get index statistics
            index_stats = self.index.describe_index_stats()
            
            return {
                "total_vectors": index_stats.get("total_vector_count", 0),
                "total_files": len(index_stats.get("namespaces", {})),
                "index_name": self.index_name,
                "embedding_model": self.model_name,
                "embedding_dimension": self.embedding_dimension,
                "index_size_bytes": index_stats.get("index_fullness", 0),
                "last_updated": datetime.utcnow().isoformat(),
                "health_status": "healthy",
                "namespaces": index_stats.get("namespaces", {})
            }
            
        except Exception as e:
            logger.error(f"Failed to get RAG stats: {str(e)}")
            return {
                "total_vectors": 0,
                "total_files": 0,
                "index_name": self.index_name,
                "embedding_model": self.model_name,
                "embedding_dimension": self.embedding_dimension,
                "health_status": "unhealthy",
                "error": str(e)
            }
    
    async def delete_file_vectors(self, file_id: str) -> Dict[str, Any]:
        """
        Delete all vectors for a specific file
        """
        try:
            logger.info(f"Deleting vectors for file: {file_id}")
            
            if not self.index:
                await self.initialize()
            
            # Delete vectors by file_id filter
            delete_response = self.index.delete(
                filter={"file_id": file_id}
            )
            
            logger.info(f"Deleted vectors for file {file_id}")
            
            return {
                "file_id": file_id,
                "success": True,
                "message": f"Successfully deleted vectors for file {file_id}",
                "deleted_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to delete vectors for file {file_id}: {str(e)}")
            return {
                "file_id": file_id,
                "success": False,
                "error": str(e),
                "deleted_at": datetime.utcnow().isoformat()
            }
    
    async def enforce_diversity(
        self, 
        results: List[Dict[str, Any]], 
        diversity_threshold: float = 0.7,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Enforce diversity in search results to avoid redundant information
        
        Args:
            results: Original search results
            diversity_threshold: Minimum diversity score (0-1)
            max_results: Maximum number of diverse results
            
        Returns:
            List of diverse results
        """
        try:
            logger.info(f"Enforcing diversity on {len(results)} results")
            
            if not results:
                return results
            
            diverse_results = [results[0]]  # Always include the top result
            
            for candidate in results[1:]:
                if len(diverse_results) >= max_results:
                    break
                
                # Check similarity with already selected results
                is_diverse = True
                for selected in diverse_results:
                    similarity = self._calculate_text_similarity(
                        candidate.get("text", ""), 
                        selected.get("text", "")
                    )
                    
                    if similarity > (1 - diversity_threshold):
                        is_diverse = False
                        break
                
                if is_diverse:
                    diverse_results.append(candidate)
            
            logger.info(f"Selected {len(diverse_results)} diverse results")
            return diverse_results
            
        except Exception as e:
            logger.error(f"Diversity enforcement failed: {str(e)}")
            return results[:max_results]  # Fallback to original results
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using simple word overlap
        """
        try:
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            if not union:
                return 0.0
            
            return len(intersection) / len(union)
            
        except Exception as e:
            logger.error(f"Text similarity calculation failed: {str(e)}")
            return 0.0

# Global RAG service instance
_rag_service: Optional[RAGService] = None

def get_rag_service() -> RAGService:
    """
    Get a singleton instance of the RAG service
    
    Returns:
        RAGService: Configured RAG service instance
    """
    global _rag_service
    
    if _rag_service is None:
        _rag_service = RAGService()
        logger.info("RAG service instance created")
    
    return _rag_service

async def get_rag_service_async() -> RAGService:
    """
    Async wrapper for getting RAG service instance
    
    Returns:
        RAGService: Configured RAG service instance
    """
    return get_rag_service()
