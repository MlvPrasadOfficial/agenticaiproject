"""
Direct SQL Agent Test Script
----------------------------
This script directly tests the SQL Agent without going through the full orchestration.
"""

import sys
import os
import asyncio
import pandas as pd
from datetime import datetime
import json
import time

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import the SQL Agent
from app.agents.sql_agent import SQLAgent

async def test_sql_agent_directly():
    """Test the SQL Agent directly without going through the API"""
    print("🧪 Testing SQL Agent directly...")
    
    # Load sample data
    try:
        df = pd.read_csv("sample_sales_data.csv")
        print(f"✅ Loaded CSV with {len(df)} rows, {len(df.columns)} columns")
        print(f"✅ Columns: {list(df.columns)}")
        print(f"✅ Sample data:")
        print(df.head(3))
        
        # Prepare data for the agent
        file_data = {
            "columns": list(df.columns),
            "data": df.to_dict('records'),
            "shape": df.shape,
            "dtypes": {str(k): str(v) for k, v in df.dtypes.to_dict().items()}
        }
        
        # Prepare state
        state = {
            "session_id": f"test_{int(time.time())}",
            "user_query": "SELECT category, SUM(sales_amount) as total_sales FROM data GROUP BY category ORDER BY total_sales DESC",
            "file_context": {"file_id": "test_file_id"},
            "file_data": file_data,
            "query_type": "sql"
        }
        
        # Initialize and run the agent
        sql_agent = SQLAgent()
        print("🧪 Running SQL Agent...")
        start_time = time.time()
        
        # Set a timeout for the agent execution
        try:
            result = await asyncio.wait_for(sql_agent.execute(state), timeout=20)
            execution_time = time.time() - start_time
            
            print(f"✅ SQL Agent completed in {execution_time:.2f} seconds")
            print(f"✅ Result keys: {list(result.keys())}")
            
            if "data" in result:
                print("\n✅ SQL QUERY SUCCESS:")
                print("-" * 60)
                for row in result["data"][:5]:  # Show first 5 rows
                    print(row)
                print("-" * 60)
            else:
                print(f"❌ No data in result. Result: {json.dumps(result, indent=2)}")
                
        except asyncio.TimeoutError:
            print("❌ SQL Agent execution timed out after 20 seconds")
            print("This could indicate an issue with the SQL agent processing logic")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_sql_agent_directly())
