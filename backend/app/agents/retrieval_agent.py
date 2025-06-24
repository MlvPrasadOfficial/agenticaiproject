# Retrieval Agent - Vector Search and Knowledge Retrieval

from typing import Dict, Any, List, Optional
import json
import numpy as np
from datetime import datetime
import asyncio
from sentence_transformers import SentenceTransformer
import pinecone
from pathlib import Path

from app.agents.base_agent import BaseAgent
from app.core.config import settings


class RetrievalAgent(BaseAgent):
    """Vector search and knowledge retrieval specialist using Pinecone"""
    
    def __init__(self):
        super().__init__("Retrieval Agent")
        self.embedding_model = None
        self.pinecone_index = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize embedding model and Pinecone connection"""
        try:
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize Pinecone (using legacy API)
            if hasattr(settings, 'PINECONE_API_KEY') and settings.PINECONE_API_KEY:
                pinecone.init(
                    api_key=settings.PINECONE_API_KEY,
                    environment=getattr(settings, 'PINECONE_ENVIRONMENT', 'us-west1-gcp')
                )
                
                index_name = getattr(settings, 'PINECONE_INDEX_NAME', 'enterprise-insights')
                if index_name in pinecone.list_indexes():
                    self.pinecone_index = pinecone.Index(index_name)
                else:
                    print(f"⚠️ Pinecone index '{index_name}' not found. Vector search will be limited.")
            else:
                print("⚠️ Pinecone API key not configured. Vector search will be simulated.")
                
        except Exception as e:
            print(f"⚠️ Error initializing RetrievalAgent components: {e}")
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute retrieval operations based on query and context"""
        
        if not self.validate_input(state):
            return {"error": "Invalid input for Retrieval Agent"}
        
        query = state.get("query", "")
        context_type = state.get("context_type", "general")
        max_results = state.get("max_results", 5)
        
        try:
            # Generate embeddings for query
            query_embedding = await self._generate_embedding(query)
            
            # Perform vector search
            search_results = await self._vector_search(
                query_embedding, 
                max_results=max_results,
                context_type=context_type
            )
            
            # Rank and filter results
            ranked_results = await self._rank_results(search_results, query)
            
            # Format response
            response = {
                "agent": self.name,
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "context_type": context_type,
                "results": ranked_results,
                "total_results": len(ranked_results),
                "search_metadata": {
                    "embedding_model": "all-MiniLM-L6-v2",
                    "vector_dimension": 384,
                    "search_type": "semantic_similarity"
                }
            }
            
            return response
            
        except Exception as e:
            error_msg = f"Error in retrieval execution: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embeddings for text using SentenceTransformer"""
        try:
            if self.embedding_model is None:
                raise ValueError("Embedding model not initialized")
            
            # Run embedding generation in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None, 
                lambda: self.embedding_model.encode([text])
            )
            
            return embedding[0].tolist()
            
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Return dummy embedding if model fails
            return [0.0] * 384
    
    async def _vector_search(self, query_embedding: List[float], max_results: int = 5, context_type: str = "general") -> List[Dict[str, Any]]:
        """Perform vector search in Pinecone or simulate if not available"""
        try:
            if self.pinecone_index is not None:
                # Real Pinecone search
                search_response = self.pinecone_index.query(
                    vector=query_embedding,
                    top_k=max_results,
                    include_metadata=True,
                    filter={"context_type": context_type} if context_type != "general" else None
                )
                
                results = []
                for match in search_response.matches:
                    results.append({
                        "id": match.id,
                        "score": float(match.score),
                        "content": match.metadata.get("content", ""),
                        "source": match.metadata.get("source", "unknown"),
                        "metadata": match.metadata
                    })
                
                return results
            else:
                # Simulated search for development
                return await self._simulate_vector_search(query_embedding, max_results, context_type)
                
        except Exception as e:
            print(f"Error in vector search: {e}")
            return await self._simulate_vector_search(query_embedding, max_results, context_type)
    
    async def _simulate_vector_search(self, query_embedding: List[float], max_results: int, context_type: str) -> List[Dict[str, Any]]:
        """Simulate vector search results for development/testing"""
        
        # Mock knowledge base entries
        mock_knowledge = [
            {
                "id": "kb_001",
                "content": "Revenue analysis shows quarterly growth trends with seasonal variations in Q4.",
                "source": "Financial Reports 2023",
                "score": 0.95,
                "metadata": {"type": "financial", "date": "2023-12-01"}
            },
            {
                "id": "kb_002", 
                "content": "Customer segmentation analysis reveals three primary demographics driving sales.",
                "source": "Market Research Database",
                "score": 0.87,
                "metadata": {"type": "marketing", "date": "2023-11-15"}
            },
            {
                "id": "kb_003",
                "content": "Product performance metrics indicate strong growth in enterprise solutions.",
                "source": "Product Analytics Dashboard",
                "score": 0.82,
                "metadata": {"type": "product", "date": "2023-10-20"}
            },
            {
                "id": "kb_004",
                "content": "Regional sales data shows highest performance in North American markets.",
                "source": "Sales Performance Reports",
                "score": 0.78,
                "metadata": {"type": "sales", "date": "2023-09-30"}
            },
            {
                "id": "kb_005",
                "content": "Operational efficiency metrics demonstrate cost reduction opportunities.",
                "source": "Operations Analytics",
                "score": 0.74,
                "metadata": {"type": "operations", "date": "2023-08-15"}
            }
        ]
        
        # Filter by context type if specified
        if context_type != "general":
            mock_knowledge = [
                item for item in mock_knowledge 
                if item["metadata"].get("type") == context_type
            ]
        
        # Return top results
        return mock_knowledge[:max_results]
    
    async def _rank_results(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Rank and enhance search results"""
        try:
            # Sort by relevance score (highest first)
            ranked_results = sorted(results, key=lambda x: x.get("score", 0), reverse=True)
            
            # Add ranking information
            for i, result in enumerate(ranked_results):
                result["rank"] = i + 1
                result["relevance"] = "high" if result.get("score", 0) > 0.8 else "medium" if result.get("score", 0) > 0.6 else "low"
            
            return ranked_results
            
        except Exception as e:
            print(f"Error ranking results: {e}")
            return results
    
    async def store_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Store document in vector database"""
        try:
            content = document.get("content", "")
            metadata = document.get("metadata", {})
            doc_id = document.get("id", f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            # Generate embedding
            embedding = await self._generate_embedding(content)
            
            if self.pinecone_index is not None:
                # Store in Pinecone
                self.pinecone_index.upsert([
                    (doc_id, embedding, metadata)
                ])
                
                return {
                    "status": "success",
                    "document_id": doc_id,
                    "message": "Document stored in vector database"
                }
            else:
                return {
                    "status": "simulated",
                    "document_id": doc_id,
                    "message": "Document storage simulated (Pinecone not configured)"
                }
                
        except Exception as e:
            error_msg = f"Error storing document: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}
    
    def get_required_fields(self) -> List[str]:
        """Get list of required fields in state"""
        return ["query"]
    
    def validate_input(self, state: Dict[str, Any]) -> bool:
        """Validate input for retrieval operations"""
        if not isinstance(state, dict):
            return False
        
        # Check for required query
        query = state.get("query")
        if not query or not isinstance(query, str) or len(query.strip()) == 0:
            return False
        
        return True
