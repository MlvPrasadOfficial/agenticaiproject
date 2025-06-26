"""
Create a new Pinecone index for testing
"""

import os
import sys
from dotenv import load_dotenv
import time

# Load environment variables directly
env_path = os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')
print(f"Loading .env file from: {env_path}")
load_dotenv(env_path)

def create_pinecone_index():
    """Create a new Pinecone index"""
    
    # Direct API key for testing
    api_key = "pcsk_7UADAM_BWX1euMKfW5mc9FsisyTE42nKFZmV9uLEaHgPa2RB6Y2K5H2Q3oMbRiDFB66She"
    environment = os.getenv('PINECONE_ENVIRONMENT', 'us-east-1-aws')
    target_index = os.getenv('PINECONE_INDEX_NAME', 'pineindex')
    
    print(f"Using Pinecone API Key: {api_key[:10]}...{api_key[-5:]}")
    print(f"Environment: {environment}")
    print(f"Target index name: {target_index}")
    
    # Try with legacy client (v2) first as it's more likely to be installed
    try:
        import pinecone
        
        # Initialize Pinecone
        pinecone.init(api_key=api_key, environment=environment)
        print("✅ Initialized Pinecone client successfully")
        
        # Check if index already exists
        indexes = pinecone.list_indexes()
        if target_index in indexes:
            print(f"⚠️ Index '{target_index}' already exists")
            return
        
        # Create a new index
        print(f"🔧 Creating new index: '{target_index}'...")
        pinecone.create_index(
            name=target_index,
            dimension=1536,  # OpenAI's embeddings dimension
            metric='cosine'
        )
          # Wait for the index to be ready
        print("⏳ Waiting for index to initialize...")
        while target_index not in pinecone.list_indexes():
            time.sleep(1)
            
        print(f"✅ Index '{target_index}' created successfully!")
        
        # Connect to the index
        index = pinecone.Index(target_index)
        stats = index.describe_index_stats()
        print(f"📊 Index stats: {stats}")
        
    except Exception as e:
        print(f"❌ Error creating Pinecone index: {e}")

if __name__ == "__main__":
    create_pinecone_index()
