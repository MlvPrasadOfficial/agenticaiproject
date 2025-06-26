#!/usr/bin/env python3
"""
Test Enhanced Vector Count Logging
Test the new before/after embedding vector counts
"""

import requests
import json
import sys
import os

def test_enhanced_vector_logging():
    """Test enhanced vector count logging with before/after embedding"""
    print("🧪 Testing Enhanced Vector Count Logging")
    print("=" * 60)
    
    backend_url = "http://localhost:8000"
    
    # Test 1: Check backend health
    try:
        health_response = requests.get(f"{backend_url}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Backend is running")
        else:
            print(f"❌ Backend not available: {health_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return
    
    # Test 2: Test embedding status endpoint with real file
    print("\n📊 Testing embedding status endpoint...")
    
    # First, let's see what files are available in uploads
    try:
        # Look for any uploaded files
        upload_dir = "uploads"
        if os.path.exists(upload_dir):
            files = os.listdir(upload_dir)
            if files:
                # Use the first file we find
                test_file = files[0]
                # Extract file_id (everything before the first underscore)
                if '_' in test_file:
                    file_id = test_file.split('_')[0]
                else:
                    file_id = test_file.replace('.csv', '')
                
                print(f"📁 Found file: {test_file}")
                print(f"🔍 Using file_id: {file_id}")
                
                # Test the new embedding status endpoint
                embedding_response = requests.get(
                    f"{backend_url}/api/v1/agents/embedding-status/{file_id}", 
                    timeout=10
                )
                
                if embedding_response.status_code == 200:
                    data = embedding_response.json()
                    print("✅ Embedding status endpoint working!")
                    
                    print(f"\n📊 Embedding Analysis for: {data.get('filename', 'unknown')}")
                    embedding_status = data.get('embedding_status', {})
                    
                    print(f"🔢 Vectors before embedding: {embedding_status.get('vectors_before_embedding', 'N/A')}")
                    print(f"🔢 Estimated vectors after: {embedding_status.get('estimated_vectors_after_embedding', 'N/A')}")
                    print(f"➕ Estimated vectors to add: {embedding_status.get('estimated_vectors_to_add', 'N/A')}")
                    
                    data_info = embedding_status.get('data_info', {})
                    print(f"📋 Data: {data_info.get('rows', 'N/A')} rows × {data_info.get('columns', 'N/A')} columns")
                    
                    chunk_breakdown = embedding_status.get('chunk_breakdown', {})
                    print(f"📦 Chunk breakdown:")
                    print(f"   - Column info chunks: {chunk_breakdown.get('column_info_chunks', 'N/A')}")
                    print(f"   - Summary chunks: {chunk_breakdown.get('summary_chunks', 'N/A')}")
                    print(f"   - Sample data chunks: {chunk_breakdown.get('sample_data_chunks', 'N/A')}")
                    print(f"   - Total estimated: {chunk_breakdown.get('total_estimated', 'N/A')}")
                    
                    print(f"🔗 Pinecone status: {data.get('pinecone_status', 'unknown')}")
                    
                elif embedding_response.status_code == 404:
                    print(f"ℹ️ File not found with ID: {file_id}")
                else:
                    print(f"❌ Embedding status failed: {embedding_response.status_code}")
                    print(f"Response: {embedding_response.text}")
            else:
                print("ℹ️ No files found in uploads directory")
        else:
            print("ℹ️ Uploads directory not found")
            
    except Exception as e:
        print(f"❌ Error testing embedding status: {e}")
    
    # Test 3: Test enhanced agent status endpoint
    print("\n📊 Testing enhanced agent status...")
    
    try:
        # Test with a dummy file_id to see the output format
        status_response = requests.get(
            f"{backend_url}/api/v1/agents/query-status/test_session", 
            timeout=10
        )
        
        if status_response.status_code == 200:
            data = status_response.json()
            retrieval_outputs = data.get('agents', {}).get('retrieval-agent', {}).get('outputs', [])
            
            print("✅ Query status endpoint working")
            print("📊 Retrieval Agent Outputs:")
            for output in retrieval_outputs:
                print(f"   - {output}")
                if any(keyword in output.lower() for keyword in ['vector', 'pinecone', 'before', 'after']):
                    print("     ✅ Contains vector count information!")
        else:
            print(f"❌ Query status failed: {status_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing query status: {e}")
    
    print("\n✅ Enhanced vector count logging test completed!")


if __name__ == "__main__":
    test_enhanced_vector_logging()
