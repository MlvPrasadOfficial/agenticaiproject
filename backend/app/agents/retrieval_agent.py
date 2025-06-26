# Retrieval Agent - Vector Search and Knowledge Retrieval

from typing import Dict, Any, List, Optional
import json
import numpy as np
from datetime import datetime
import asyncio
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, Index
from pathlib import Path

from app.agents.base_agent import BaseAgent
from app.core.config import settings


class RetrievalAgent(BaseAgent):
    """Vector search and knowledge retrieval specialist using Pinecone"""
    def __init__(self):
        super().__init__("Retrieval Agent")
        self.name = "Retrieval Agent"  # Add explicit name attribute
        self.embedding_model = None
        self.pinecone_index = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize embedding model and Pinecone connection"""
        try:
            # Initialize embedding model (1024 dimensions to match Pinecone index)
            self.embedding_model = SentenceTransformer('all-roberta-large-v1')
            print("✅ Using all-roberta-large-v1 model (1024 dimensions)")
            
            # Initialize Pinecone (using new v3.0+ API)
            if hasattr(settings, 'PINECONE_API_KEY') and settings.PINECONE_API_KEY:
                pc = Pinecone(api_key=settings.PINECONE_API_KEY)
                
                index_name = getattr(settings, 'PINECONE_INDEX_NAME', 'enterprise-insights')
                
                # List existing indexes
                indexes = pc.list_indexes()
                index_names = [idx.name for idx in indexes]
                
                if index_name in index_names:
                    self.pinecone_index = pc.Index(index_name)
                    print(f"✅ Connected to Pinecone index: {index_name}")
                else:
                    print(f"⚠️ Pinecone index '{index_name}' not found. Available indexes: {index_names}")
            else:
                print("⚠️ Pinecone API key not configured. Vector search will be simulated.")
                
        except Exception as e:
            print(f"⚠️ Error initializing RetrievalAgent components: {e}")
            import traceback
            traceback.print_exc()
    
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
                "total_results": len(ranked_results),                "search_metadata": {
                    "embedding_model": "all-roberta-large-v1",
                    "vector_dimension": 1024,
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
    
    async def index_file_data(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Index file data into Pinecone vector store during upload"""
        try:
            file_path = state.get("file_path")
            data_profile = state.get("data_profile", {})
            
            if not file_path:
                return {"error": "No file path provided for indexing"}
            
            print(f"🔄 Indexing file data from: {file_path}")
            
            # Get vector count before indexing
            vectors_before = await self._get_pinecone_vector_count()
            print(f"📊 Pinecone vectors before indexing: {vectors_before}")
            
            # Load and chunk the data for indexing
            chunks = await self._prepare_file_chunks(file_path, data_profile)
            
            if not chunks:
                return {
                    "status": "no_data",
                    "message": "No data chunks to index",
                    "vectors_added": 0,
                    "vectors_before": vectors_before,
                    "vectors_after": vectors_before
                }
            
            # Generate embeddings and store in Pinecone
            vectors_added = 0
            batch_size = 50  # Process in batches
            
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                await self._index_chunk_batch(batch, file_path)
                vectors_added += len(batch)
            
            # Get vector count after indexing
            vectors_after = await self._get_pinecone_vector_count()
            print(f"📊 Pinecone vectors after indexing: {vectors_after} (added: {vectors_after - vectors_before})")
            
            return {
                "status": "success",
                "file_path": file_path,
                "vectors_added": vectors_added,
                "total_chunks": len(chunks),
                "vectors_before": vectors_before,
                "vectors_after": vectors_after,
                "actual_vectors_added": vectors_after - vectors_before,
                "agent": self.name,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Error indexing file data: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}
    
    async def _prepare_file_chunks(self, file_path: str, data_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prepare data chunks from file for vector indexing"""
        try:
            import pandas as pd
            
            # Load the file
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                print(f"⚠️ Unsupported file type for indexing: {file_path}")
                return []
            
            chunks = []
            
            # Create chunks from the data
            # 1. Column descriptions
            for col in df.columns:
                col_info = {
                    "content": f"Column '{col}': {df[col].dtype}, sample values: {df[col].dropna().head(3).tolist()}",
                    "metadata": {
                        "type": "column_info",
                        "column_name": col,
                        "file_path": file_path,
                        "data_type": str(df[col].dtype)
                    }
                }
                chunks.append(col_info)
            
            # 2. Summary statistics
            if 'summary_statistics' in data_profile:
                stats = data_profile['summary_statistics']
                stats_content = f"Data summary: {len(df)} rows, {len(df.columns)} columns. "
                if isinstance(stats, dict):
                    stats_content += " ".join([f"{k}: {v}" for k, v in stats.items() if isinstance(v, (str, int, float))])
                
                chunks.append({
                    "content": stats_content,
                    "metadata": {
                        "type": "data_summary", 
                        "file_path": file_path,
                        "rows": len(df),
                        "columns": len(df.columns)
                    }
                })
            
            # 3. Sample data rows (first few rows as context)
            for idx in range(min(5, len(df))):
                row_content = f"Sample row {idx + 1}: " + ", ".join([f"{col}={df.iloc[idx][col]}" for col in df.columns[:5]])  # Limit to first 5 columns
                chunks.append({
                    "content": row_content,
                    "metadata": {
                        "type": "sample_data",
                        "file_path": file_path,
                        "row_index": idx
                    }
                })
            
            print(f"✅ Prepared {len(chunks)} chunks for indexing")
            return chunks
            
        except Exception as e:
            print(f"❌ Error preparing file chunks: {e}")
            return []
    
    async def _index_chunk_batch(self, batch: List[Dict[str, Any]], file_path: str):
        """Index a batch of chunks into Pinecone"""
        try:
            if self.pinecone_index is None:
                print("⚠️ Pinecone index not available, skipping indexing")
                return
            
            vectors_to_upsert = []            
            for i, chunk in enumerate(batch):
                # Generate embedding
                embedding = await self._generate_embedding(chunk["content"])
                
                # Create unique ID
                chunk_id = f"{file_path}_{chunk['metadata']['type']}_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                # Prepare metadata
                metadata = chunk["metadata"].copy()
                metadata["content"] = chunk["content"]
                metadata["indexed_at"] = datetime.now().isoformat()
                
                vectors_to_upsert.append((chunk_id, embedding, metadata))
            
            # Upsert to Pinecone
            self.pinecone_index.upsert(vectors_to_upsert)
            print(f"✅ Indexed batch of {len(batch)} chunks")
            
        except Exception as e:
            print(f"❌ Error indexing chunk batch: {e}")
    
    async def _get_pinecone_vector_count(self) -> int:
        """Get the current number of vectors in the Pinecone index"""
        try:
            if self.pinecone_index is None:
                print("⚠️ Pinecone index not available, returning 0 for vector count")
                return 0
            
            # Get index stats
            stats = self.pinecone_index.describe_index_stats()
            total_vectors = stats.get('total_vector_count', 0)
            
            return total_vectors
            
        except Exception as e:
            print(f"❌ Error getting Pinecone vector count: {e}")
            return 0
    
    def get_required_fields(self) -> List[str]:
        """Get list of required fields in state"""
        return ["query"]  # For execute method, file_path for index_file_data method
