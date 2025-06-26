#!/usr/bin/env python3
"""
Simple Test for Vector Count Functionality
Direct test of retrieval agent vector count methods
"""

import os
import sys
import asyncio

# Add backend to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

async def simple_vector_test():
    """Simple test to verify vector count methods work"""
    print("🧪 Simple Vector Count Test")
    print("=" * 40)
    
    try:
        # Import the RetrievalAgent
        from app.agents.retrieval_agent import RetrievalAgent
        print("✅ Successfully imported RetrievalAgent")
        
        # Initialize the agent
        agent = RetrievalAgent()
        print("✅ Successfully initialized RetrievalAgent")
        
        # Test the vector count method
        print("\n📊 Testing vector count method...")
        vector_count = await agent._get_pinecone_vector_count()
        print(f"Current vector count: {vector_count}")
        
        if isinstance(vector_count, int) and vector_count >= 0:
            print("✅ Vector count method working correctly")
        else:
            print("⚠️ Vector count method returned unexpected value")
        
        print("\n✅ Simple vector count test completed successfully!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("This is normal if Pinecone/dependencies aren't configured")
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(simple_vector_test())
