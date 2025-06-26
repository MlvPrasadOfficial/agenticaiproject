import asyncio
import sys
import os
import time
import pandas as pd

# Update path to handle being in the tests directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.agents.sql_agent import SQLAgent

async def test_sql_agent():
    """Test the SQL agent directly with sample data"""
    
    try:
        print("🔍 Testing SQL Agent directly...")
        agent = SQLAgent()
        
        # Load sample data
        csv_path = "../sample_sales_data.csv"
        if not os.path.exists(csv_path):
            print(f"❌ Sample data not found at {csv_path}")
            return
            
        df = pd.read_csv(csv_path)
        print(f"📊 Loaded data: {df.shape[0]} rows, {df.columns.tolist()}")
        
        # Convert to dictionary format for agent
        file_data = {
            "columns": list(df.columns),
            "data": df.to_dict('records'),
            "shape": df.shape,
            "dtypes": {str(k): str(v) for k, v in df.dtypes.items()}  # Convert dtypes to strings
        }
        
        # Create minimal test state
        test_state = {
            "user_query": "SELECT category, SUM(sales_amount) as total_sales FROM data GROUP BY category ORDER BY total_sales DESC",
            "session_id": "direct_test_session",
            "file_data": file_data
        }
        
        # Execute the agent directly with timeout
        start_time = time.time()
        print("⏱️ Starting SQL Agent execution...")
        
        try:
            # Use asyncio.wait_for to enforce timeout
            result = await asyncio.wait_for(
                agent.execute(test_state), 
                timeout=30  # 30 second timeout
            )
            
            execution_time = time.time() - start_time
            print(f"⏱️ SQL Agent completed in {execution_time:.2f} seconds")
            
            print("🔍 SQL Agent result:")
            print(result)
            
            if 'data' in result:
                print("\nResults data:")
                for row in result['data'][:5]:  # Show first 5 rows
                    print(row)
            
            return result
        except asyncio.TimeoutError:
            print("⏱️ SQL Agent timed out after 30 seconds")
            return None
        
    except Exception as e:
        print(f"❌ Error testing SQL Agent: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_sql_agent())
