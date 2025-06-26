#!/usr/bin/env python3
"""
Simple Pinecone v3 client test script.
Uses Pinecone Python client v3.0.0
"""

import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv(dotenv_path='../backend/.env')

# Get credentials from environment
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_HOST = os.getenv("PINECONE_HOST")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "pineindex")

print(f"API Key: {PINECONE_API_KEY[:10]}...")
print(f"Host: {PINECONE_HOST}")
print(f"Index Name: {INDEX_NAME}")

try:
    import pinecone
    print(f"Pinecone Version: {pinecone.__version__}")
    
    # Create Pinecone client (v3.0.0 API)
    print("\nCreating Pinecone client...")
    pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
    print("✅ Pinecone client created")
    
    # List all indexes
    print("\nListing indexes...")
    try:
        indexes = pc.list_indexes()
        index_names = [idx.name for idx in indexes]
        print("=== Available Indexes ===")
        print(f"Found {len(indexes)} indexes")
        for idx in indexes:
            print(f"- {idx.name} (host: {idx.host})")
    except Exception as e:
        print(f"Error listing indexes: {e}")
        index_names = []
        
    # Try to connect to the index with the provided host
    try:
        print(f"\nConnecting to index '{INDEX_NAME}'...")
        if PINECONE_HOST:
            # Try connecting using host URL directly
            index = pc.Index(
                name=INDEX_NAME,
                host=PINECONE_HOST
            )
            print("✅ Connected to index using host URL")
            
            # Get index stats
            stats = index.describe_index_stats()
            print("\nIndex Stats:")
            print(stats)
        else:
            print("❌ No host URL provided for direct index connection")
            
            # Try to find the index in the list if available
            if INDEX_NAME in index_names:
                index = pc.Index(INDEX_NAME)
                print(f"✅ Connected to index '{INDEX_NAME}'")
                
                # Get index stats
                stats = index.describe_index_stats()
                print("\nIndex Stats:")
                print(stats)
            else:
                print(f"❌ Index '{INDEX_NAME}' not found in available indexes")
                
    except Exception as e:
        print(f"Error connecting to index: {e}")

except ImportError as ie:
    print(f"❌ Error importing pinecone: {ie}")
    print("Make sure you have pinecone-client v3.0.0 installed")
    print("Run: pip install pinecone-client==3.0.0")
except Exception as e:
    print(f"❌ Error: {e}")
