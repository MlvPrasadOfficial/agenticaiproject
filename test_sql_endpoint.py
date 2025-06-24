"""
Simplified SQL Query Test Script
--------------------------------
This script tests just the SQL endpoint directly
"""

import requests
import json
import time

BACKEND_URL = "http://localhost:8000"

def test_sql_endpoint(timeout=20):
    """Test SQL endpoint directly"""
    print("🧪 Testing SQL Endpoint directly...")
    
    # Upload file first
    with open("sample_sales_data.csv", 'rb') as file:
        files = {'file': ("sample_sales_data.csv", file, 'text/csv')}
        upload_response = requests.post(f"{BACKEND_URL}/api/v1/upload", files=files)
    
    if upload_response.status_code != 200:
        print(f"❌ Upload failed: {upload_response.text}")
        return
    
    upload_result = upload_response.json()
    file_id = upload_result['file_id']
    print(f"✅ File uploaded: {file_id}")
    
    # Send SQL query directly
    query_payload = {
        "query": "SELECT category, SUM(sales_amount) as total_sales FROM data GROUP BY category ORDER BY total_sales DESC",
        "file_id": file_id,
        "query_type": "sql",
        "timestamp": int(time.time()),
        "bypass_orchestrator": True  # Hint to bypass orchestrator if supported
    }
    
    print(f"🔍 Sending SQL query: {query_payload['query']}")
    print(f"⏱️ Timeout set to {timeout} seconds")
    
    try:
        start_time = time.time()
        query_response = requests.post(
            f"{BACKEND_URL}/api/v1/query/sql_direct",  # Direct SQL endpoint
            json=query_payload, 
            timeout=timeout
        )
        execution_time = time.time() - start_time
        
        print(f"⏱️ Query completed in {execution_time:.2f} seconds")
        print(f"🔍 Response status: {query_response.status_code}")
        
        if query_response.status_code == 200:
            result = query_response.json()
            print("🔍 Full response:")
            print(json.dumps(result, indent=2))
            
            # Check for SQL data
            if "data" in result:
                print("\n✅ SQL QUERY SUCCESS:")
                print("-" * 60)
                for row in result["data"][:5]:  # Show first 5 rows
                    print(row)
                print("-" * 60)
            else:
                print(f"❌ No data in response.")
        else:
            print(f"❌ Query failed: {query_response.text}")
            
    except requests.exceptions.Timeout:
        print(f"⏱️ Query timed out after {timeout} seconds!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sql_endpoint()
