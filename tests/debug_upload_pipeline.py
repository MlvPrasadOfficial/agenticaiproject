#!/usr/bin/env python3
"""
Debug file upload and data agent processing
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.data_processor import DataProcessor
from app.services.agent_orchestrator import AgentOrchestrator
from app.agents.data_agent import DataAgent
from app.agents.retrieval_agent import RetrievalAgent
from pinecone import Pinecone

# Load environment
load_dotenv('backend/.env')

async def test_data_agent_directly():
    """Test Data Agent directly with a file"""
    print("🔍 Testing Data Agent directly...")
    
    # Create a simple test file
    test_file = "sample_sales_data.csv"
    if not os.path.exists(test_file):
        print("❌ Sample file not found")
        return False
    
    # Initialize components
    data_agent = DataAgent()
    
    # Create state with file data
    state = {
        "session_id": "test_session",
        "file_path": test_file,
        "query_type": "data_exploration"
    }
    
    print(f"📁 Processing file: {test_file}")
    
    try:
        # Execute data agent
        result = await data_agent.execute(state)
        print(f"✅ Data Agent Result: {result}")
        return True
    except Exception as e:
        print(f"❌ Data Agent Error: {e}")
        return False

async def test_retrieval_agent_directly():
    """Test Retrieval Agent directly"""
    print("\n🔍 Testing Retrieval Agent directly...")
    
    # Check Pinecone before
    pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
    index = pc.Index('pineindex')
    stats_before = index.describe_index_stats()
    print(f"📊 Vectors before: {stats_before['total_vector_count']}")
    
    # Initialize retrieval agent
    retrieval_agent = RetrievalAgent()
    
    # Create state with some sample data
    state = {
        "session_id": "test_session",
        "file_path": "sample_sales_data.csv",
        "data_insights": "Sample sales data with product categories and regions",
        "query_type": "data_exploration"
    }
    
    try:
        # Execute retrieval agent
        result = await retrieval_agent.execute(state)
        print(f"✅ Retrieval Agent Result: {result}")
        
        # Check Pinecone after
        stats_after = index.describe_index_stats()
        print(f"📊 Vectors after: {stats_after['total_vector_count']}")
        
        if stats_after['total_vector_count'] > stats_before['total_vector_count']:
            print("🎉 SUCCESS: Vectors were added!")
            return True
        else:
            print("❌ FAILURE: No vectors were added")
            return False
            
    except Exception as e:
        print(f"❌ Retrieval Agent Error: {e}")
        return False

async def test_upload_processing():
    """Test the upload processing pipeline"""
    print("\n🔍 Testing Upload Processing Pipeline...")
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    
    # Create file data
    file_data = {
        "file_path": "sample_sales_data.csv",
        "file_type": "csv",
        "columns": ["date", "product", "category", "region", "sales_amount", "quantity"],
        "row_count": 100
    }
    
    try:
        result = await orchestrator.trigger_upload_agents(
            file_id="test_file_123",
            file_data=file_data
        )
        print(f"✅ Upload Processing Result: {result}")
        return True
    except Exception as e:
        print(f"❌ Upload Processing Error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Testing File Upload and Pinecone Indexing Pipeline")
    print("=" * 60)
    
    # Test individual components
    data_agent_ok = await test_data_agent_directly()
    retrieval_agent_ok = await test_retrieval_agent_directly()
    upload_processing_ok = await test_upload_processing()
    
    print("\n" + "=" * 60)
    print("📊 RESULTS:")
    print(f"  Data Agent: {'✅ WORKING' if data_agent_ok else '❌ FAILED'}")
    print(f"  Retrieval Agent: {'✅ WORKING' if retrieval_agent_ok else '❌ FAILED'}")
    print(f"  Upload Processing: {'✅ WORKING' if upload_processing_ok else '❌ FAILED'}")
    
    if data_agent_ok and retrieval_agent_ok:
        print("🎉 File upload pipeline should work!")
    else:
        print("❌ File upload pipeline has issues")

if __name__ == "__main__":
    asyncio.run(main())
