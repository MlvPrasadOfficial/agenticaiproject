#!/usr/bin/env python3
"""
Simple script to check Pinecone connection and list available indexes.
"""

import os
from dotenv import load_dotenv
import sys

# Load environment variables from the backend .env file
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', '.env')
print(f"Loading .env from: {env_path}")
load_dotenv(env_path)

def check_pinecone():
    """Check Pinecone connection and list available indexes with both client versions."""
    
    # Get credentials from environment
    api_key = os.getenv('PINECONE_API_KEY')
    environment = os.getenv('PINECONE_ENVIRONMENT')
    host = os.getenv('PINECONE_HOST')
    index_name = os.getenv('PINECONE_INDEX_NAME', 'pineindex')
    
    if not api_key:
        print("❌ No PINECONE_API_KEY found in environment.")
        return
        
    print(f"🔑 Using API Key: {api_key[:10]}...")
    print(f"🌎 Environment: {environment}")
    print(f"🏠 Host URL: {host}")
    print(f"📚 Index Name: {index_name}")
      # Try with new Pinecone client (v3+)
    try:
        print("\n----- Testing with Pinecone client v3+ -----")
        from pinecone import Pinecone
        
        # Initialize client
        pc = Pinecone(api_key=api_key)
        print("✅ Successfully initialized Pinecone client v3+")
        
        # List indexes
        indexes = pc.list_indexes()
        if indexes:
            print(f"📋 Available indexes: {[idx.name for idx in indexes]}")
            for idx in indexes:
                print(f"  - {idx.name} (host: {idx.host})")
        else:
            print("📋 No indexes found with this API key.")
            
        # Try to connect to the index directly with the host URL if available
        if host and index_name:
            try:
                print(f"\n🔄 Attempting direct connection to {index_name} using host URL...")
                index = pc.Index(
                    name=index_name,
                    host=host
                )
                stats = index.describe_index_stats()
                print("✅ Successfully connected to index using host URL!")
                print(f"📊 Index stats: {stats}")
            except Exception as e:
                print(f"❌ Error connecting to index using host URL: {e}")
    
    except ImportError:
        print("⚠️ Pinecone client v3+ not found. This is the newer client version.")
    except Exception as e:
        print(f"❌ Error with Pinecone client v3+: {e}")
      # Try with legacy Pinecone client (v2)
    try:
        print("\n----- Testing with Pinecone client v2 (legacy) -----")
        import pinecone
        
        # Initialize client
        pinecone.init(api_key=api_key, environment=environment)
        print("✅ Successfully initialized legacy Pinecone client")
        
        # List indexes
        indexes = pinecone.list_indexes()
        if indexes:
            print(f"📋 Available indexes: {indexes}")
            for idx in indexes:
                print(f"  - {idx}")
        else:
            print("📋 No indexes found with this API key.")
            
        # Try to connect to the index directly if it's defined
        if index_name:
            try:
                print(f"\n🔄 Attempting direct connection to {index_name}...")
                index = pinecone.Index(index_name)
                stats = index.describe_index_stats()
                print("✅ Successfully connected to index!")
                print(f"📊 Index stats: {stats}")
            except Exception as e:
                print(f"❌ Error connecting to index: {e}")
            
    except ImportError:
        print("⚠️ Legacy Pinecone client not found.")
    except Exception as e:
        print(f"❌ Error with legacy Pinecone client: {e}")

if __name__ == "__main__":
    print("===== CHECKING PINECONE CONNECTION =====")
    check_pinecone()
