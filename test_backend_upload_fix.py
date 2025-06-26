#!/usr/bin/env python3
"""
Test script to verify the backend upload endpoint is working correctly
"""

import requests
import os
import json

def test_backend_upload():
    """Test the backend upload functionality"""
    
    # Test health check first
    print("🏥 Testing health check...")
    try:
        health_response = requests.get("http://localhost:8000/health")
        if health_response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {health_response.json()}")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Create a test CSV file
    test_csv_content = """Name,Age,Department,Salary
John Doe,30,Engineering,75000
Jane Smith,28,Marketing,65000
Bob Johnson,35,Sales,70000
Alice Williams,32,HR,60000
Charlie Brown,29,Engineering,72000"""
    
    test_file_path = "test_upload.csv"
    with open(test_file_path, 'w') as f:
        f.write(test_csv_content)
    
    print("\n📁 Testing file upload...")
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': (test_file_path, f, 'text/csv')}
            upload_response = requests.post("http://localhost:8000/upload", files=files)
        
        if upload_response.status_code == 200:
            print("✅ Upload successful")
            response_data = upload_response.json()
            print(f"   File ID: {response_data.get('file_id')}")
            print(f"   Filename: {response_data.get('filename')}")
            print(f"   Rows: {response_data.get('rows')}")
            print(f"   Columns: {response_data.get('columns')}")
            
            # Print preview data
            preview = response_data.get('preview_data', {})
            if preview:
                print(f"   Preview columns: {preview.get('columns', [])}")
                print(f"   Sample rows: {len(preview.get('sample_rows', []))}")
            
            return True
        else:
            print(f"❌ Upload failed: {upload_response.status_code}")
            print(f"   Error: {upload_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
    
    return False

def test_query_endpoint():
    """Test the query endpoint"""
    print("\n💬 Testing query endpoint...")
    try:
        query_data = {
            "query": "What is the average salary?",
            "file_id": "test_file_id"
        }
        
        query_response = requests.post(
            "http://localhost:8000/query",
            json=query_data,
            headers={"Content-Type": "application/json"}
        )
        
        if query_response.status_code == 200:
            print("✅ Query endpoint accessible")
            print(f"   Response: {query_response.json()}")
            return True
        else:
            print(f"❌ Query failed: {query_response.status_code}")
            print(f"   Error: {query_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Query error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Backend Upload Functionality")
    print("=" * 50)
    
    upload_success = test_backend_upload()
    query_success = test_query_endpoint()
    
    print("\n📊 Test Results:")
    print(f"Upload Test: {'✅ PASS' if upload_success else '❌ FAIL'}")
    print(f"Query Test: {'✅ PASS' if query_success else '❌ FAIL'}")
    
    if upload_success and query_success:
        print("\n🎉 All tests passed! Backend is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the backend logs for details.")
