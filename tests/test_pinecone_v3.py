#!/usr/bin/env python3
"""
Test script for Pinecone client v3.0.0 connection.
"""

import os
from dotenv import load_dotenv
import sys

# Load environment variables from the backend .env file
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', '.env')
print(f"Loading .env from: {env_path}")
load_dotenv(env_path)

def test_pinecone_v3():
    """Test Pinecone connection with v3 client."""
    
    # Get credentials from environment
    api_key = os.getenv('PINECONE_API_KEY')
    index_name = os.getenv('PINECONE_INDEX_NAME', 'pineindex')
    host = os.getenv('PINECONE_HOST')
    
    if not api_key:
        print("❌ No PINECONE_API_KEY found in environment.")
        return
          print(f"🔑 Using API Key: {api_key[:10]}...")
    print(f"📚 Target Index Name: {index_name}")
    print(f"🏠 Host URL: {host}")
    
    try:
        import pinecone
        print(f"📦 Pinecone client version: {pinecone.__version__}")
        
        # Initialize Pinecone - v3 uses a different API
        print("\n1️⃣ Initializing Pinecone...")
        pc = pinecone.Pinecone(api_key=api_key)
        print("✅ Successfully initialized Pinecone")
        
        # List indexes with v3 API
        try:
            print("\n2️⃣ Listing indexes...")
            indexes = pc.list_indexes()
            if indexes:
                print(f"📋 Indexes: {[idx.name for idx in indexes]}")
                for idx in indexes:
                    print(f"  - {idx.name} (host: {idx.host})")
            else:
                print("📋 No indexes found with this API key.")
        except Exception as e:
            print(f"❌ Error listing indexes: {e}")
            
        # Try to connect to the index directly using the host URL
        if host and index_name:
            try:
                print(f"\n4️⃣ Attempting to connect to index '{index_name}' using host URL...")
                index = pinecone.Index(
                    name=index_name,
                    host=host
                )
                print("✅ Successfully connected to index!")
                
                # Get index stats
                stats = index.describe_index_stats()
                print(f"📊 Index stats: {stats}")
                
                # Test simple query
                print("\n5️⃣ Testing vector search...")
                dimension = 1536  # Standard dimension for many embeddings
                test_vector = [0.0] * dimension
                
                results = index.query(
                    vector=test_vector,
                    top_k=1,
                    include_metadata=True
                )
                
                print(f"🔍 Query results: {results}")
                
            except Exception as e:
                print(f"❌ Error connecting to index: {e}")
                
    except Exception as e:
        print(f"❌ Pinecone connection failed: {e}")

if __name__ == "__main__":
    print("===== TESTING PINECONE V3 CLIENT CONNECTION =====")
    test_pinecone_v3()
    print("\n✅ Test completed!")
