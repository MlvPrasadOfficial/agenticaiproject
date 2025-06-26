#!/usr/bin/env python3
"""Test Pinecone connection with both legacy and new client APIs"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

def test_pinecone():
    try:
        api_key = os.getenv('PINECONE_API_KEY')
        environment = os.getenv('PINECONE_ENVIRONMENT', 'us-east-1-aws')
        target_index = os.getenv('PINECONE_INDEX_NAME', 'pineindex')
        
        if not api_key:
            print("❌ No PINECONE_API_KEY found in environment")
            return False
            
        print(f"🔍 Testing with API key: {api_key[:20]}...")
        print(f"🔍 Environment: {environment}")
        print(f"🔍 Target index name: {target_index}")
        
        # Test with new client (v3+) first
        try:
            print("\n=== Testing with new Pinecone Python client (v3+) ===")
            from pinecone import Pinecone
            
            # Initialize Pinecone
            pc = Pinecone(api_key=api_key)
            print("✅ Pinecone v3+ client initialized successfully!")
            
            # List indexes
            indexes = pc.list_indexes()
            index_names = [idx.name for idx in indexes]
            print(f"📋 Available indexes: {index_names}")
            
            # Check if our index exists
            if target_index in index_names:
                print(f"✅ Index '{target_index}' found!")
                
                # Connect to the index
                index = pc.Index(target_index)
                stats = index.describe_index_stats()
                print(f"📊 Index stats: {stats}")
                
            else:
                print(f"⚠️ Index '{target_index}' not found. Available indexes: {index_names}")
                
        except ImportError:
            print("⚠️ New Pinecone client not available, falling back to legacy client")
        except Exception as e:
            print(f"❌ Error with new Pinecone client: {e}")
        
        # Test with legacy client (v2)
        try:
            print("\n=== Testing with legacy Pinecone client (v2) ===")
            import pinecone
            
            # Initialize Pinecone
            pinecone.init(api_key=api_key, environment=environment)
            print("✅ Pinecone legacy client initialized successfully!")
            
            # List indexes
            indexes = pinecone.list_indexes()
            print(f"📋 Available indexes: {indexes}")
            
            # Check if our index exists
            if target_index in indexes:
                print(f"✅ Index '{target_index}' found!")
                
                # Connect to the index
                index = pinecone.Index(target_index)
                stats = index.describe_index_stats()
                print(f"📊 Index stats: {stats}")
                
            else:
                print(f"⚠️ Index '{target_index}' not found. Available: {indexes}")
        
        except ImportError:
            print("⚠️ Legacy Pinecone client not available")
        except Exception as e:
            print(f"❌ Error with legacy Pinecone client: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ Pinecone connection failed: {e}")
        return False

if __name__ == "__main__":
    print("\n=== PINECONE CONNECTION TEST ===")
    success = test_pinecone()
    
    if success:
        print("\n✅ Pinecone configuration test completed!")
    else:
        print("\n❌ Pinecone configuration test failed!")
