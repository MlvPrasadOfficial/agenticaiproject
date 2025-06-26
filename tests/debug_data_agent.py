#!/usr/bin/env python3
"""
Debug Data Agent execution specifically
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.agents.data_agent import DataAgent

# Load environment
load_dotenv('backend/.env')

async def test_data_agent_execution():
    """Test Data Agent with actual file"""
    print("🔍 Testing Data Agent execution...")
    
    # Check if sample file exists
    test_file = "sample_sales_data.csv"
    if not os.path.exists(test_file):
        print("❌ Sample file not found")
        return False
    
    print(f"📁 Testing with file: {test_file}")
    
    # Initialize Data Agent
    data_agent = DataAgent()
    
    # Create state like the orchestrator would
    state = {
        "session_id": "test_session",
        "file_path": test_file,
        "query_type": "data_exploration"
    }
    
    print(f"📋 State: {state}")
    
    try:
        # Execute data agent
        print("\n🔄 Executing Data Agent...")
        import time
        start_time = time.time()
        
        result = await data_agent.execute(state)
        
        execution_time = time.time() - start_time
        print(f"⏱️ Execution time: {execution_time:.2f}s")
        
        if result:
            print(f"✅ Data Agent Result Keys: {list(result.keys())}")
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
                return False
            
            if "data_profile" in result:
                profile = result["data_profile"]
                print(f"📊 Data Profile Keys: {list(profile.keys()) if isinstance(profile, dict) else 'Not a dict'}")
                
                if isinstance(profile, dict) and "basic_info" in profile:
                    basic_info = profile["basic_info"]
                    print(f"📈 Basic Info: {basic_info}")
                
                print("🎉 Data Agent produced meaningful output!")
                return True
            else:
                print("❌ No data_profile in result")
                return False
        else:
            print("❌ No result from Data Agent")
            return False
            
    except Exception as e:
        print(f"❌ Data Agent Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the test"""
    print("🚀 Data Agent Debug Test")
    print("=" * 50)
    
    success = await test_data_agent_execution()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Data Agent: WORKING")
        print("   → Can process files and generate data profiles")
    else:
        print("❌ Data Agent: BROKEN")
        print("   → Need to debug further")

if __name__ == "__main__":
    asyncio.run(main())
