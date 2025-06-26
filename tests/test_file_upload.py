#!/usr/bin/env python3
"""Test file upload functionality"""

import requests
import os
import sys
import json
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Backend URL
BACKEND_URL = "http://localhost:8000"

def check_server_health():
    """Check if the backend server is running"""
    try:
        backend_health = requests.get(f"{BACKEND_URL}/api/v1/health").json()
        print("✅ Backend Status:", backend_health)
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Backend server not running!")
        return False

def test_file_upload():
    """Test file upload functionality"""
    
    # Check server health first
    if not check_server_health():
        print("Please start the backend server first!")
        return False
    
    # Test file upload
    try:
        print("🔍 Testing file upload...")
        
        # Path to sample data file
        file_path = os.path.join(os.path.dirname(__file__), '..', 'sample_sales_data.csv')
        if not os.path.exists(file_path):
            print(f"❌ Sample data file not found at: {file_path}")
            return False
            
        with open(file_path, 'rb') as file:
            files = {'file': ("sample_sales_data.csv", file, 'text/csv')}
            upload_response = requests.post(f"{BACKEND_URL}/api/v1/upload", files=files)
        
        if upload_response.status_code != 200:
            print(f"❌ Upload failed: {upload_response.text}")
            return False
        
        # Get upload result
        upload_result = upload_response.json()
        file_id = upload_result.get('file_id')
        
        if not file_id:
            print(f"❌ No file_id in response: {upload_result}")
            return False
        
        print(f"✅ File uploaded successfully! file_id: {file_id}")
        
        # Check if the uploaded file can be used in a query
        print("\n🔍 Testing query with uploaded file...")
        
        # Simple SQL query
        query_payload = {
            "query": "SELECT * FROM data LIMIT 5",
            "file_id": file_id,
            "query_type": "sql",
            "timestamp": int(time.time())
        }
        
        print(f"🔍 Sending SQL query: {query_payload['query']}")
        query_response = requests.post(f"{BACKEND_URL}/api/v1/query", json=query_payload, timeout=30)
        
        if query_response.status_code != 200:
            print(f"❌ Query failed: {query_response.text}")
            return False
        
        result = query_response.json()
        print("📊 Query result:")
        print(json.dumps(result, indent=2)[:500] + "...") # Show truncated result
        
        # Check if the file was saved in the uploads directory
        print("\n🔍 Checking if file was saved in uploads directory...")
        uploads_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'uploads')
        
        if not os.path.exists(uploads_dir):
            print(f"⚠️ Uploads directory not found at: {uploads_dir}")
        else:
            # Check if any file with this ID exists
            matching_files = [f for f in os.listdir(uploads_dir) if file_id in f]
            if matching_files:
                print(f"✅ Found uploaded file in uploads directory: {matching_files}")
            else:
                print(f"⚠️ No matching file found in uploads directory for ID: {file_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in file upload test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n=== FILE UPLOAD TEST ===")
    success = test_file_upload()
    
    if success:
        print("\n✅ File upload test completed successfully!")
    else:
        print("\n❌ File upload test failed!")
