"""
Simple script to check Pinecone indexes with both v2 and v3 clients
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables directly
env_path = os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')
print(f"Loading .env file from: {env_path}")
load_dotenv(env_path)

def check_pinecone_indexes():
    """Check available Pinecone indexes with both client versions"""
    
    # Direct API key for testing
    api_key = "pcsk_7UADAM_BWX1euMKfW5mc9FsisyTE42nKFZmV9uLEaHgPa2RB6Y2K5H2Q3oMbRiDFB66She"
    environment = os.getenv('PINECONE_ENVIRONMENT', 'us-east-1-aws')
    
    print(f"Using Pinecone API Key: {api_key[:10]}...{api_key[-5:]}")
    print(f"Environment: {environment}")
    
    # Try with Pinecone v3 client first
    try:
        print("\n=== Testing with Pinecone v3 client ===")
        from pinecone import Pinecone
        
        # Initialize client
        pc = Pinecone(api_key=api_key)
        print("✅ Initialized Pinecone v3 client successfully")
        
        # List indexes
        indexes = pc.list_indexes()
        print(f"Found {len(indexes)} indexes:")
        
        # Display index details
        for i, index in enumerate(indexes):
            print(f"{i+1}. Index name: {index.name}")
            print(f"   Host: {index.host}")
            # Additional details if available
            for attr in ['dimension', 'metric', 'spec', 'status']:
                if hasattr(index, attr):
                    print(f"   {attr.capitalize()}: {getattr(index, attr)}")
            print("")
            
    except ImportError:
        print("❌ Pinecone v3 client not available")
    except Exception as e:
        print(f"❌ Error with Pinecone v3 client: {e}")
    
    # Try with legacy Pinecone client (v2)
    try:
        print("\n=== Testing with Pinecone v2 client ===")
        import pinecone
        
        # Initialize legacy client
        pinecone.init(api_key=api_key, environment=environment)
        print("✅ Initialized Pinecone v2 client successfully")
        
        # List indexes
        indexes = pinecone.list_indexes()
        print(f"Found {len(indexes)} indexes: {indexes}")
        
        # Try to describe each index
        for idx_name in indexes:
            try:
                index = pinecone.Index(idx_name)
                stats = index.describe_index_stats()
                print(f"\nIndex: {idx_name}")
                print(f"Stats: {stats}")
            except Exception as e:
                print(f"Could not get details for index {idx_name}: {e}")
                
    except ImportError:
        print("❌ Pinecone v2 client not available")
    except Exception as e:
        print(f"❌ Error with Pinecone v2 client: {e}")

if __name__ == "__main__":
    check_pinecone_indexes()
