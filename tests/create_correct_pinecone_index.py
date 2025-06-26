#!/usr/bin/env python3

import sys
import os

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_path)

from pinecone import Pinecone, ServerlessSpec
from app.core.config import settings

def create_correct_index():
    """Create a new Pinecone index with the correct dimensions"""
    
    print("🚀 Creating Pinecone Index with Correct Dimensions")
    print("=" * 60)
    
    try:
        # Initialize Pinecone
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        
        # Check current embedding model dimensions
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')  # This is what we're using
        sample_embedding = model.encode(["test"])
        dimensions = len(sample_embedding[0])
        print(f"📐 Current embedding model dimensions: {dimensions}")
        
        # Check existing indexes
        indexes = pc.list_indexes()
        print("📋 Existing indexes:")
        for idx in indexes:
            print(f"   - {idx.name}: {idx.dimension} dimensions")
        
        # Create new index with correct dimensions
        new_index_name = "enterprise-insights-384"
        
        if new_index_name not in [idx.name for idx in indexes]:
            print(f"\n🔨 Creating new index '{new_index_name}' with {dimensions} dimensions...")
            
            pc.create_index(
                name=new_index_name,
                dimension=dimensions,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            print(f"✅ Index '{new_index_name}' created successfully!")
            print(f"💡 Update PINECONE_INDEX_NAME in config to '{new_index_name}'")
        else:
            print(f"✅ Index '{new_index_name}' already exists")
            
    except Exception as e:
        print(f"❌ Error creating index: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_correct_index()
