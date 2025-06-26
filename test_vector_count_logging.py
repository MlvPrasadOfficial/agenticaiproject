#!/usr/bin/env python3
"""
Test Vector Count Logging in Retrieval Agent
Test the new vector count logging functionality added to the Retrieval Agent
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from app.agents.retrieval_agent import RetrievalAgent
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


async def test_vector_count_logging():
    """Test vector count logging functionality"""
    print("🧪 Testing Vector Count Logging in Retrieval Agent")
    print("=" * 60)
    
    # Initialize Retrieval Agent
    try:
        retrieval_agent = RetrievalAgent()
        print("✅ Retrieval Agent initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing Retrieval Agent: {e}")
        return
    
    # Test 1: Check current vector count
    print("\n📊 Test 1: Getting current vector count")
    try:
        vector_count = await retrieval_agent._get_pinecone_vector_count()
        print(f"Current Pinecone vector count: {vector_count}")
    except Exception as e:
        print(f"❌ Error getting vector count: {e}")
    
    # Test 2: Simulate file indexing with vector count logging
    print("\n📊 Test 2: Simulating file indexing with vector logging")
    
    # Create a simple test file
    test_data = """name,age,city
John,25,New York
Jane,30,Los Angeles
Bob,35,Chicago
Alice,28,Boston"""
    
    test_file_path = "sample_test_data.csv"
    try:
        # Write test file synchronously (acceptable for test)
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_data)
        print(f"✅ Created test file: {test_file_path}")
        
        # Test indexing with logging
        state = {
            "file_path": test_file_path,
            "data_profile": {
                "summary_statistics": {
                    "rows": 4,
                    "columns": 3
                }
            }
        }
        
        result = await retrieval_agent.index_file_data(state)
        
        print("\n📊 Indexing Result:")
        print(f"  Status: {result.get('status')}")
        print(f"  Vectors before: {result.get('vectors_before', 'N/A')}")
        print(f"  Vectors after: {result.get('vectors_after', 'N/A')}")
        print(f"  Vectors added (reported): {result.get('vectors_added', 'N/A')}")
        print(f"  Actual vectors added: {result.get('actual_vectors_added', 'N/A')}")
        print(f"  Total chunks: {result.get('total_chunks', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error during indexing test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            print(f"✅ Cleaned up test file: {test_file_path}")
    
    print("\n✅ Vector count logging test completed!")


if __name__ == "__main__":
    asyncio.run(test_vector_count_logging())
