#!/usr/bin/env python3
"""
Simple test for query endpoint debugging
"""

import requests
import json

def test_query_simple():
    """Test the query endpoint with minimal data"""
    
    print("💬 Testing query endpoint...")
    try:
        query_data = {
            "query": "What is the average salary?",
            "file_id": "test_file_id"
        }
        
        print(f"Sending: {query_data}")
        
        query_response = requests.post(
            "http://localhost:8000/query",
            json=query_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {query_response.status_code}")
        print(f"Response Headers: {query_response.headers}")
        
        if query_response.status_code == 200:
            print("✅ Query successful")
            print(f"Response: {query_response.json()}")
        else:
            print(f"❌ Query failed: {query_response.status_code}")
            print(f"Error: {query_response.text}")
            
    except Exception as e:
        print(f"❌ Query error: {e}")

if __name__ == "__main__":
    test_query_simple()
