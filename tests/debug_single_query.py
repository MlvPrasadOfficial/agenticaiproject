import requests
import json
import time
import os
import sys

# Add path for imports if needed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Test single query with detailed debugging - Focus on SQL
BACKEND_URL = "http://localhost:8000"

def check_server_health():
    """Check if the backend server is running"""
    try:
        backend_health = requests.get(f"{BACKEND_URL}/api/v1/health").json()
        print("✅ Backend Status:", backend_health)
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Backend server not running!")
        return False

def test_single_query(timeout=30):
    """Test a single SQL query with detailed debugging and timeout"""
    # Check server health
    if not check_server_health():
        print("Please start the backend server first!")
        return
    
    # First upload file
    print("🔍 Testing single SQL query with detailed debugging...")
    
    with open("../sample_sales_data.csv", 'rb') as file:
        files = {'file': ("sample_sales_data.csv", file, 'text/csv')}
        upload_response = requests.post(f"{BACKEND_URL}/api/v1/upload", files=files)
    
    if upload_response.status_code != 200:
        print(f"❌ Upload failed: {upload_response.text}")
        return
    
    upload_result = upload_response.json()
    file_id = upload_result['file_id']
    print(f"✅ File uploaded: {file_id}")
    
    # Test specific SQL query
    query_payload = {
        "query": "SELECT category, SUM(sales_amount) as total_sales FROM data GROUP BY category ORDER BY total_sales DESC",
        "file_id": file_id,
        "query_type": "sql",
        "timestamp": int(time.time())
    }
    print(f"🔍 Sending SQL query: {query_payload['query']}")
    print(f"⏱️ Timeout set to {timeout} seconds")
    
    try:
        start_time = time.time()
        query_response = requests.post(f"{BACKEND_URL}/api/v1/query", json=query_payload, timeout=timeout)
        execution_time = time.time() - start_time
        
        print(f"⏱️ Query completed in {execution_time:.2f} seconds")
        print(f"🔍 Query response status: {query_response.status_code}")
        
        if query_response.status_code == 200:
            result = query_response.json()
            print("🔍 Full response:")
            print(json.dumps(result, indent=2))
            
            # Check specifically for SQL data in the response
            if result and 'result' in result:
                agent_outputs = result['result'].get('agent_outputs', {})
                sql_output = agent_outputs.get('sql', {})
                
                if sql_output and 'data' in sql_output:
                    print("\n✅ SQL QUERY SUCCESS:")
                    print("-" * 60)
                    for row in sql_output['data'][:10]:  # Show first 10 rows
                        print(row)
                    print("-" * 60)
                else:
                    print("\n❌ SQL QUERY RETURNED NO DATA")
                    # Debug check
                    print(f"Available agent outputs: {list(agent_outputs.keys())}")
                    if 'sql' in agent_outputs:
                        print(f"SQL agent output keys: {list(agent_outputs['sql'].keys())}")
        else:
            print(f"❌ Query failed: {query_response.text}")
    
    except requests.exceptions.Timeout:
        print(f"⏱️ Query timed out after {timeout} seconds!")
        print("Possible issues:")
        print("- SQL agent may be stuck in execution")
        print("- Agent orchestrator might not be propagating results")
        print("- Database connection issue")
    except Exception as e:
        print(f"❌ Error during query: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_single_query(timeout=30)  # Set timeout to 30 seconds
