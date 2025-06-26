#!/usr/bin/env python3
"""
Debug script to test upload and see exact API response format
"""

import requests
import json

def test_upload_response():
    """Test upload endpoint and show exact response structure"""
    
    # Create test data
    test_data = """Name,Age,Department,Salary
John Doe,30,Engineering,75000
Jane Smith,28,Marketing,65000
Bob Johnson,35,Sales,70000"""
    
    # Write to temporary file
    with open('temp_test.csv', 'w') as f:
        f.write(test_data)
    
    print("📁 Testing upload response format...")
    
    try:
        with open('temp_test.csv', 'rb') as f:
            files = {'file': ('temp_test.csv', f, 'text/csv')}
            response = requests.post("http://localhost:8000/upload", files=files)
        
        if response.status_code == 200:
            print("✅ Upload successful!")
            data = response.json()
            
            print("\n📊 Full Response:")
            print(json.dumps(data, indent=2))
            
            print("\n🔍 Preview Data Structure:")
            preview = data.get('preview_data', {})
            print(f"  Columns: {preview.get('columns', [])}")
            print(f"  Rows: {preview.get('rows', [])}")
            print(f"  Number of rows: {len(preview.get('rows', []))}")
            
            if preview.get('rows'):
                print(f"\n📋 First row sample:")
                print(f"  {preview['rows'][0]}")
            
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Cleanup
    import os
    if os.path.exists('temp_test.csv'):
        os.remove('temp_test.csv')

if __name__ == "__main__":
    test_upload_response()
