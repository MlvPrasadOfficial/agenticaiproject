#!/usr/bin/env python3
"""
Test script to verify the new Pinecone API key is working correctly.
"""
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

def test_pinecone_connection():
    """Test Pinecone connection with new API key."""
    try:
        # Try new pinecone package first
        try:
            from pinecone import Pinecone
            use_new_client = True
        except ImportError:
            # Fall back to older pinecone-client
            import pinecone
            use_new_client = False
        
        # Get configuration
        api_key = os.getenv('PINECONE_API_KEY')
        environment = os.getenv('PINECONE_ENVIRONMENT', 'us-east-1-aws')
        print(f"Testing Pinecone API Key: {api_key[:20]}...")
        
        if use_new_client:
            # New Pinecone client (v3+)
            pc = Pinecone(api_key=api_key)
            indexes = pc.list_indexes()
            print("✅ Pinecone connection successful!")
            print(f"Available indexes: {[idx.name for idx in indexes]}")
            
            # Check if our target index exists
            target_index = os.getenv('PINECONE_INDEX_NAME', 'pineindex')
            index_names = [idx.name for idx in indexes]
            
            if target_index in index_names:
                print(f"✅ Target index '{target_index}' found!")
                index = pc.Index(target_index)
                stats = index.describe_index_stats()
                print(f"Index stats: {stats}")
            else:
                print(f"⚠️  Target index '{target_index}' not found.")
                print(f"Available indexes: {index_names}")
        else:
            # Old pinecone-client (v2)
            pinecone.init(api_key=api_key, environment=environment)
            indexes = pinecone.list_indexes()
            print("✅ Pinecone connection successful!")
            print(f"Available indexes: {indexes}")
            
            # Check if our target index exists
            target_index = os.getenv('PINECONE_INDEX_NAME', 'pineindex')
            
            if target_index in indexes:
                print(f"✅ Target index '{target_index}' found!")
                index = pinecone.Index(target_index)
                stats = index.describe_index_stats()
                print(f"Index stats: {stats}")
            else:
                print(f"⚠️  Target index '{target_index}' not found.")
                print(f"Available indexes: {indexes}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pinecone connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing new Pinecone API key...")
    success = test_pinecone_connection()
    
    if success:
        print("\n✅ Pinecone configuration is working!")
    else:
        print("\n❌ Pinecone configuration needs attention.")
