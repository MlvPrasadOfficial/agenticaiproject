#!/usr/bin/env python3
"""
Detailed insight query test to see what agents were used
"""

import requests
import json
import time
import os

BACKEND_URL = "http://localhost:8000"

def test_detailed_insight_query():
    """Test insight query with detailed output"""
    
    # Upload file first
    file_path = "../sample_sales_data.csv"
    with open(file_path, 'rb') as file:
        files = {'file': ("sample_sales_data.csv", file, 'text/csv')}
        upload_response = requests.post(f"{BACKEND_URL}/api/v1/upload", files=files)
    
    upload_result = upload_response.json()
    file_id = upload_result.get('file_id')
    print(f"✅ File uploaded: {file_id}")
    
    # Test insight query
    print("\n🔍 Testing detailed insight query...")
    insight_query = {
        "query": "Analyze this sales data and provide insights about customer patterns",
        "file_id": file_id,
        "query_type": "insight",
        "timestamp": int(time.time())
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/v1/query", json=insight_query, timeout=120)
        if response.status_code == 200:
            result = response.json()
            print("✅ Insight query successful")
            
            # Print the full response structure
            print("\n📊 FULL RESPONSE:")
            print(json.dumps(result, indent=2))
            
            # Check agent outputs specifically
            if 'result' in result and 'agent_outputs' in result['result']:
                agent_outputs = result['result']['agent_outputs']
                print(f"\n🤖 Agents executed: {list(agent_outputs.keys())}")
                
                for agent_name, agent_output in agent_outputs.items():
                    print(f"\n🔍 {agent_name.upper()} AGENT OUTPUT:")
                    print(json.dumps(agent_output, indent=2)[:500] + "..." if len(str(agent_output)) > 500 else json.dumps(agent_output, indent=2))
            
            # Check if retrieval agent was specifically used
            if 'result' in result and 'agent_outputs' in result['result']:
                agent_outputs = result['result']['agent_outputs']
                if 'retrieval' in agent_outputs:
                    print("\n🎯 RETRIEVAL AGENT WAS EXECUTED!")
                    retrieval_data = agent_outputs['retrieval']
                    print(f"Retrieval result: {retrieval_data}")
                else:
                    print("\n⚠️ Retrieval agent was NOT executed")
                    print("This means Pinecone integration is not being triggered")
        else:
            print(f"❌ Insight query failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Insight query error: {e}")

if __name__ == "__main__":
    test_detailed_insight_query()
