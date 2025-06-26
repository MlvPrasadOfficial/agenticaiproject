#!/usr/bin/env python3
"""
Test execution order and check Pinecone vectors before/after
"""

import os
import requests
import json
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment
load_dotenv('backend/.env')

def check_pinecone_vectors():
    """Check current vector count in Pinecone"""
    try:
        pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        index = pc.Index('pineindex')
        stats = index.describe_index_stats()
        return stats['total_vector_count']
    except Exception as e:
        print(f"❌ Error checking Pinecone: {e}")
        return None

def test_query_execution():
    """Test actual query execution and track vector changes"""
    
    print("🚀 Testing Query Execution and Vector Changes")
    print("=" * 60)
    
    # Check vectors BEFORE
    vectors_before = check_pinecone_vectors()
    print(f"📊 Vectors BEFORE query: {vectors_before}")
    
    # Upload file first
    print("\n1️⃣ Uploading file...")
    try:
        with open('sample_sales_data.csv', 'rb') as f:
            files = {'file': f}
            response = requests.post('http://localhost:8000/api/v1/upload', files=files, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            file_id = result['file_id']
            print(f"✅ File uploaded: {file_id}")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return
    
    # Check vectors AFTER upload
    vectors_after_upload = check_pinecone_vectors()
    print(f"📊 Vectors AFTER upload: {vectors_after_upload}")
    
    # Execute a query
    print("\n2️⃣ Executing SQL query...")
    query_data = {
        "query": "Show total sales by region",
        "file_context": {"file_id": file_id}
    }
    
    try:
        response = requests.post(
            'http://localhost:8000/api/v1/query', 
            json=query_data, 
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Query executed successfully")
            
            # Check if we have agent execution details
            if 'agent_outputs' in result:
                print("\n📋 Agent Execution Order and Results:")
                for agent, output in result['agent_outputs'].items():
                    if output:
                        status = "✅" if output else "❌"
                        print(f"  {status} {agent.upper()}: {str(output)[:100]}...")
            
        else:
            print(f"❌ Query failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Query error: {e}")
    
    # Check vectors AFTER query
    vectors_after_query = check_pinecone_vectors()
    print(f"\n📊 Vectors AFTER query: {vectors_after_query}")
    
    # Summary
    print(f"\n" + "=" * 60)
    print("📊 VECTOR CHANGE SUMMARY:")
    print(f"  Before: {vectors_before}")
    print(f"  After Upload: {vectors_after_upload}")
    print(f"  After Query: {vectors_after_query}")
    
    if vectors_after_query > vectors_before:
        print("🎉 SUCCESS: Vectors were added to Pinecone!")
    else:
        print("❌ FAILURE: No vectors were added to Pinecone")

if __name__ == "__main__":
    test_query_execution()
