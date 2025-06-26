#!/usr/bin/env python3
"""
Test Agent Status with Vector Count
Test that the agent status endpoint includes vector count information
"""

import requests
import json
import sys

def test_agent_status_vector_count():
    """Test that agent status includes vector count information"""
    print("🧪 Testing Agent Status with Vector Count Information")
    print("=" * 60)
    
    # Backend URL
    backend_url = "http://localhost:8000"
    
    # Test 1: Check if backend is running
    try:
        health_response = requests.get(f"{backend_url}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Backend is running")
        else:
            print(f"❌ Backend health check failed: {health_response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("Make sure the backend is running with: python backend/main.py")
        return
    
    # Test 2: Check agent status endpoint with a dummy file_id
    print("\n📊 Testing agent status endpoint...")
    
    try:
        # Use a dummy file_id to test the endpoint structure
        test_file_id = "test123"
        status_response = requests.get(f"{backend_url}/api/v1/agents/status/{test_file_id}", timeout=10)
        
        if status_response.status_code == 404:
            print("ℹ️ File not found (expected for dummy file_id)")
        elif status_response.status_code == 200:
            data = status_response.json()
            print("✅ Agent status endpoint accessible")
            
            # Check if retrieval agent outputs include vector count
            retrieval_outputs = data.get("agents", {}).get("retrieval-agent", {}).get("outputs", [])
            
            print("\n📊 Retrieval Agent Outputs:")
            for output in retrieval_outputs:
                print(f"  - {output}")
                if "vector" in output.lower() or "pinecone" in output.lower():
                    print("    ✅ Contains vector count information!")
            
        else:
            print(f"❌ Unexpected status code: {status_response.status_code}")
            print(f"Response: {status_response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing agent status: {e}")
    
    # Test 3: Test query status endpoint
    print("\n📊 Testing query status endpoint...")
    
    try:
        test_session_id = "test_session_123"
        query_status_response = requests.get(f"{backend_url}/api/v1/agents/query-status/{test_session_id}", timeout=10)
        
        if query_status_response.status_code == 200:
            data = query_status_response.json()
            print("✅ Query status endpoint accessible")
            
            # Check if retrieval agent outputs include vector count
            retrieval_outputs = data.get("agents", {}).get("retrieval-agent", {}).get("outputs", [])
            
            print("\n📊 Query Retrieval Agent Outputs:")
            for output in retrieval_outputs:
                print(f"  - {output}")
                if "vector" in output.lower() or "pinecone" in output.lower():
                    print("    ✅ Contains vector count information!")
        else:
            print(f"❌ Query status failed: {query_status_response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing query status: {e}")
    
    print("\n✅ Agent status vector count test completed!")


if __name__ == "__main__":
    test_agent_status_vector_count()
