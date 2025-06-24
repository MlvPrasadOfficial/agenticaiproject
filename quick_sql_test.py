import requests
import json
import time
import os

# Test simplified SQL query with reduced timeout
BACKEND_URL = "http://localhost:8000"

def test_simple_sql(timeout=30):
    """Test a very simple SQL query with short timeout"""
    
    try:
        # Check server health
        health_response = requests.get(f"{BACKEND_URL}/api/v1/health")
        if health_response.status_code != 200:
            print(f"❌ Server health check failed: {health_response.status_code}")
            return
        print("✅ Backend is healthy")
        
        # Upload a file
        with open("sample_sales_data.csv", 'rb') as file:
            files = {'file': ("sample_sales_data.csv", file, 'text/csv')}
            upload_response = requests.post(f"{BACKEND_URL}/api/v1/upload", files=files)
        
        if upload_response.status_code != 200:
            print(f"❌ Upload failed: {upload_response.text}")
            return
        
        upload_result = upload_response.json()
        file_id = upload_result['file_id']
        print(f"✅ File uploaded: {file_id}")
        
        # Test with very simple query first
        simple_query = {
            "query": "Show me the first 5 rows of data",  # Natural language query
            "file_id": file_id,
            "query_type": "data",  # Not SQL type
            "timestamp": int(time.time())
        }
        print(f"🔍 Sending simple data query")
        
        # Use shorter timeout
        query_response = requests.post(f"{BACKEND_URL}/api/v1/query", 
                                      json=simple_query, 
                                      timeout=timeout)
        
        if query_response.status_code == 200:
            print("✅ Simple query succeeded!")
            # Just print keys to keep output manageable
            result = query_response.json()
            print(f"Response keys: {list(result.keys())}")
            if 'result' in result:
                print(f"Result keys: {list(result['result'].keys())}")
                if 'agent_outputs' in result['result']:
                    print(f"Agent output keys: {list(result['result']['agent_outputs'].keys())}")
        else:
            print(f"❌ Simple query failed: {query_response.status_code}")
            print(query_response.text)
    
    except requests.exceptions.Timeout:
        print(f"⏱️ Query timed out after {timeout} seconds!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_simple_sql(timeout=30)  # Short timeout
