#!/usr/bin/env python3

import sys
import os

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_path)

from pinecone import Pinecone
from app.core.config import settings

def check_pinecone_index():
    """Check Pinecone index dimensions and stats"""
    
    print("🚀 Pinecone Index Inspection")
    print("=" * 50)
    
    try:
        # Initialize Pinecone
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        
        # List indexes
        indexes = pc.list_indexes()
        print(f"📋 Available indexes:")
        for idx in indexes:
            print(f"   - {idx.name}: {idx.dimension} dimensions, {idx.metric} metric")
        
        # Get specific index info
        index_name = settings.PINECONE_INDEX_NAME
        index = pc.Index(index_name)
        
        # Get index stats
        stats = index.describe_index_stats()
        print(f"\n📊 Index '{index_name}' Stats:")
        print(f"   Dimension: {stats.get('dimension', 'unknown')}")
        print(f"   Total vectors: {stats.get('total_vector_count', 0)}")
        
        # Check if vectors exist
        namespaces = stats.get('namespaces', {})
        if namespaces:
            print(f"   Namespaces: {list(namespaces.keys())}")
            for ns, ns_stats in namespaces.items():
                print(f"     - {ns}: {ns_stats.get('vector_count', 0)} vectors")
        else:
            print("   No vectors found in index")
            
    except Exception as e:
        print(f"❌ Error checking Pinecone: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_pinecone_index()
