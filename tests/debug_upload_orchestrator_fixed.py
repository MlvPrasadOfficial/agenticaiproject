#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_path)

from app.services.agent_orchestrator import AgentOrchestrator
from app.services.data_processor import DataProcessor

async def test_upload_flow():
    """Test the actual upload flow that's failing"""
    
    print("🚀 Upload Orchestrator Debug Test")
    print("=" * 50)
      # Test with an actual uploaded file
    file_path = "../sample_sales_data.csv"
    if not os.path.exists(file_path):
        print(f"❌ Test file {file_path} not found")
        return
    
    # Simulate what the upload endpoint does
    print("🔄 Step 1: Processing file with DataProcessor...")
    processor = DataProcessor()
    file_data = await processor.process_file(file_path)
    print(f"📋 DataProcessor Result Keys: {list(file_data.keys())}")
    print(f"📁 File Path: {file_data.get('file_path')}")
    print(f"✅ Status: {file_data.get('status')}")
    
    if 'data_profile' in file_data:
        print(f"📊 Data Profile Keys: {list(file_data['data_profile'].keys())}")
        basic_info = file_data['data_profile'].get('basic_info', {})
        print(f"📈 Rows: {basic_info.get('rows', 'unknown')}")
        print(f"📈 Columns: {basic_info.get('columns', 'unknown')}")
    
    print("\n🔄 Step 2: Triggering upload agents...")
    orchestrator = AgentOrchestrator()
    
    print("🔍 DEBUG: What's being passed to trigger_upload_agents:")
    print("   file_id: 'test_file_123'")
    print(f"   file_data keys: {list(file_data.keys())}")
    print(f"   file_data['file_path']: {file_data.get('file_path')}")
    
    try:
        result = await orchestrator.trigger_upload_agents(
            file_id="test_file_123",
            file_data=file_data
        )
        print(f"✅ Upload agents completed: {list(result.keys())}")
        
        if 'data_result' in result:
            print(f"📊 Data Agent Result: {result['data_result'].get('status', 'unknown')}")
        if 'retrieval_result' in result:
            print(f"🔍 Retrieval Agent Result: {result['retrieval_result'].get('status', 'unknown')}")
            
    except Exception as e:
        print(f"❌ Error in upload agents: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_upload_flow())
