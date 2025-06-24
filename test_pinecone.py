#!/usr/bin/env python3
"""Test Pinecone connection"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

def test_pinecone():
    try:
        import pinecone
        
        api_key = os.getenv('PINECONE_API_KEY')
        environment = os.getenv('PINECONE_ENVIRONMENT', 'us-east-1-aws')
        
        if not api_key:
            print("❌ No PINECONE_API_KEY found in environment")
            return False
            
        print(f"🔍 Testing with API key: {api_key[:20]}...")
        
        # Initialize Pinecone
        pinecone.init(api_key=api_key, environment=environment)
        print("✅ Pinecone initialized successfully!")
        
        # List indexes
        indexes = pinecone.list_indexes()
        print(f"📋 Available indexes: {indexes}")
        
        # Check if our index exists
        index_name = "pineindex"
        
        if index_name in indexes:
            print(f"✅ Index '{index_name}' found!")
            
            # Connect to the index
            index = pinecone.Index(index_name)
            stats = index.describe_index_stats()
            print(f"📊 Index stats: {stats}")
            
        else:
            print(f"⚠️ Index '{index_name}' not found. Available: {indexes}")
            
        return True
        
    except Exception as e:
        print(f"❌ Pinecone connection failed: {e}")
        return False

if __name__ == "__main__":
    test_pinecone()
