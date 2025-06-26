#!/usr/bin/env python3
"""
Monitor file upload and Pinecone integration test
This script will check:
1. File upload functionality
2. Pinecone vector search integration
3. Agent orchestrator workflow
"""

import requests
import json
import time
import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv('../backend/.env')

BACKEND_URL = "http://localhost:8000"

def check_pinecone_before_upload():
    """Check Pinecone index status before upload"""
    print("🔍 Checking Pinecone index status BEFORE upload...")
    
    try:
        import pinecone
        
        # Get credentials
        api_key = os.getenv('PINECONE_API_KEY')
        host = os.getenv('PINECONE_HOST')
        index_name = os.getenv('PINECONE_INDEX_NAME', 'pineindex')
        
        # Initialize client
        pc = pinecone.Pinecone(api_key=api_key)
        
        # Connect to index using host
        if host:
            index = pc.Index(host=host)
        else:
            index = pc.Index(index_name)
            
        # Get stats
        stats = index.describe_index_stats()
        print(f"📊 BEFORE UPLOAD - Index stats: {stats}")
        return stats
        
    except Exception as e:
        print(f"❌ Error checking Pinecone: {e}")
        return None

def upload_file_and_test():
    """Upload file via API and test the workflow"""
    print("\n🔍 Testing file upload via backend API...")
    
    # Upload file
    file_path = "../sample_sales_data.csv"
    if not os.path.exists(file_path):
        print(f"❌ Sample file not found: {file_path}")
        return None
        
    with open(file_path, 'rb') as file:
        files = {'file': ("sample_sales_data.csv", file, 'text/csv')}
        upload_response = requests.post(f"{BACKEND_URL}/api/v1/upload", files=files)
    
    if upload_response.status_code != 200:
        print(f"❌ Upload failed: {upload_response.text}")
        return None
    
    upload_result = upload_response.json()
    file_id = upload_result.get('file_id')
    print(f"✅ File uploaded: {file_id}")
    
    return file_id

def test_query_with_file(file_id):
    """Test different types of queries to see agent interaction"""
    print(f"\n🔍 Testing queries with file_id: {file_id}")
    
    # Test 1: Simple SQL query
    print("\n1️⃣ Testing SQL query...")
    sql_query = {
        "query": "SELECT category, COUNT(*) as count FROM data GROUP BY category",
        "file_id": file_id,
        "query_type": "sql",
        "timestamp": int(time.time())
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/v1/query", json=sql_query, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print("✅ SQL query successful")
            print(f"📊 Result keys: {list(result.keys())}")
        else:
            print(f"❌ SQL query failed: {response.text}")
    except Exception as e:
        print(f"❌ SQL query error: {e}")
    
    # Test 2: Insight query (should trigger more agents)
    print("\n2️⃣ Testing insight query...")
    insight_query = {
        "query": "What are the key insights from this sales data?",
        "file_id": file_id,
        "query_type": "insight",
        "timestamp": int(time.time())
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/v1/query", json=insight_query, timeout=60)
        if response.status_code == 200:
            result = response.json()
            print("✅ Insight query successful")
            print(f"📊 Result keys: {list(result.keys())}")
            
            # Check if retrieval agent was used
            if 'result' in result and 'agent_outputs' in result['result']:
                agent_outputs = result['result']['agent_outputs']
                print(f"🤖 Agents used: {list(agent_outputs.keys())}")
                
                if 'retrieval' in agent_outputs:
                    print("🔍 Retrieval agent was executed!")
                    retrieval_output = agent_outputs['retrieval']
                    print(f"📋 Retrieval output: {retrieval_output}")
        else:
            print(f"❌ Insight query failed: {response.text}")
    except Exception as e:
        print(f"❌ Insight query error: {e}")

def check_pinecone_after_upload():
    """Check Pinecone index status after upload and queries"""
    print("\n🔍 Checking Pinecone index status AFTER upload and queries...")
    
    try:
        import pinecone
        
        # Get credentials
        api_key = os.getenv('PINECONE_API_KEY')
        host = os.getenv('PINECONE_HOST')
        index_name = os.getenv('PINECONE_INDEX_NAME', 'pineindex')
        
        # Initialize client
        pc = pinecone.Pinecone(api_key=api_key)
        
        # Connect to index using host
        if host:
            index = pc.Index(host=host)
        else:
            index = pc.Index(index_name)
            
        # Get stats
        stats = index.describe_index_stats()
        print(f"📊 AFTER UPLOAD - Index stats: {stats}")
        
        # Check if any vectors were added
        total_vectors = stats.get('total_vector_count', 0)
        if total_vectors > 0:
            print(f"🎉 SUCCESS! {total_vectors} vectors found in Pinecone index!")
            
            # Try a sample search
            print("\n🔍 Testing vector search...")
            try:
                # Create a simple query vector (this is just for testing)
                query_vector = [0.1] * 1024  # Dummy vector matching index dimension
                search_results = index.query(
                    vector=query_vector,
                    top_k=3,
                    include_metadata=True
                )
                print(f"🔍 Search results: {search_results}")
            except Exception as search_error:
                print(f"❌ Search error: {search_error}")
        else:
            print("⚠️ No vectors found in Pinecone index after upload")
        
        return stats
        
    except Exception as e:
        print(f"❌ Error checking Pinecone after upload: {e}")
        return None

def main():
    """Main test function"""
    print("🚀 Starting file upload and Pinecone integration test")
    print("=" * 60)
    
    # Step 1: Check Pinecone before
    before_stats = check_pinecone_before_upload()
    
    # Step 2: Upload file
    file_id = upload_file_and_test()
    if not file_id:
        return
    
    # Step 3: Test queries
    test_query_with_file(file_id)
    
    # Step 4: Check Pinecone after
    after_stats = check_pinecone_after_upload()
    
    # Step 5: Compare results
    print("\n" + "=" * 60)
    print("📊 SUMMARY:")
    
    if before_stats and after_stats:
        before_count = before_stats.get('total_vector_count', 0)
        after_count = after_stats.get('total_vector_count', 0)
        
        print(f"📈 Vectors before: {before_count}")
        print(f"📈 Vectors after: {after_count}")
        
        if after_count > before_count:
            print(f"🎉 SUCCESS! {after_count - before_count} new vectors added to Pinecone!")
        else:
            print("⚠️ No new vectors were added to Pinecone during the test")
    
    print("🏁 Test completed!")

if __name__ == "__main__":
    main()
