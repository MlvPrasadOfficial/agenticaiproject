#!/usr/bin/env python3

import sys
import os

# Add the backend directory to Python path  
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_path)

from pinecone import Pinecone
from app.core.config import settings

try:
    # Initialize Pinecone using settings
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    
    # Check the pineindex
    index = pc.Index("pineindex")
    stats = index.describe_index_stats()
    
    print(f"📊 Index 'pineindex' Status:")
    print(f"   Dimension: {stats.get('dimension', 'unknown')}")
    print(f"   Total vectors: {stats.get('total_vector_count', 0)}")
    
    if stats.get('total_vector_count', 0) > 0:
        print("🎉 SUCCESS: Vectors found in index!")
        print("✅ File upload and Pinecone indexing is now WORKING!")
    else:
        print("❌ No vectors found in index")
        
except Exception as e:
    print(f"❌ Error checking Pinecone: {e}")
