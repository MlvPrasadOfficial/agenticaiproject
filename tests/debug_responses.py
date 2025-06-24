"""
Debug Test - Check Actual Query Responses
=========================================
This will show us exactly what the system is returning
"""

import requests
import json
from pathlib import Path

BACKEND_URL = "http://localhost:8000"

def test_detailed_responses():
    """Test and show detailed responses from all queries"""
    print("🔍 DETAILED RESPONSE ANALYSIS")
    print("=" * 80)
    
    # Upload file first
    csv_file = Path("sample_sales_data.csv")
    if not csv_file.exists():
        print("❌ Sample CSV not found")
        return
    
    print("📁 Uploading file...")
    with open(csv_file, 'rb') as file:
        files = {'file': (csv_file.name, file, 'text/csv')}
        response = requests.post(f"{BACKEND_URL}/api/v1/upload", files=files)
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.text}")
        return
    
    file_id = response.json()['file_id']
    print(f"✅ File uploaded: {file_id}")
    
    # Test queries with full response analysis
    queries = [
        ("SQL Query", "SELECT category, SUM(sales_amount) as total_sales FROM data GROUP BY category ORDER BY total_sales DESC"),
        ("Natural Language Insight", "What are the key trends and patterns in sales performance?"),
        ("Chart Request", "Create a bar chart showing sales by category")
    ]
    
    for query_type, query in queries:
        print(f"\n{'='*80}")
        print(f"🔍 TESTING: {query_type}")
        print(f"Query: {query}")
        print("=" * 80)
        
        payload = {"query": query, "file_id": file_id}
        response = requests.post(f"{BACKEND_URL}/api/v1/query", json=payload, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Response received")
            print(f"📋 Response keys: {list(result.keys())}")
            
            # Print each key's content
            for key, value in result.items():
                print(f"\n🔍 {key.upper()}:")
                if isinstance(value, str):
                    if len(value) > 500:
                        print(f"   {value[:500]}... [TRUNCATED - Total length: {len(value)}]")
                    else:
                        print(f"   {value}")
                elif isinstance(value, (list, dict)):
                    print(f"   {json.dumps(value, indent=2)[:1000]}{'...' if len(str(value)) > 1000 else ''}")
                else:
                    print(f"   {value}")
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(f"Error: {response.text}")
    
    # Test Pinecone connection specifically
    print(f"\n{'='*80}")
    print("🔍 TESTING PINECONE CONNECTION")
    print("=" * 80)
    
    pinecone_test_query = "Test Pinecone vector search capabilities"
    payload = {"query": pinecone_test_query, "file_id": file_id}
    response = requests.post(f"{BACKEND_URL}/api/v1/query", json=payload, timeout=60)
    
    if response.status_code == 200:
        result = response.json()
        if 'agent_trace' in result:
            print("🔍 Agent execution trace:")
            trace = result['agent_trace']
            if isinstance(trace, str):
                print(f"   {trace}")
            else:
                print(f"   {json.dumps(trace, indent=2)}")
    
    print(f"\n{'='*80}")
    print("🎯 ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_detailed_responses()
