#!/usr/bin/env python3

"""
Test script to verify filename display fix in agent status endpoint
"""

import requests
import json
import os
import glob

def test_filename_fix():
    # Look for an uploaded file
    upload_dir = "backend/uploads"
    pattern = os.path.join(upload_dir, "*_sample_sales_data.csv")
    matching_files = glob.glob(pattern)
    
    if not matching_files:
        print("❌ No sample_sales_data.csv files found")
        return
    
    # Get the file_id from the filename
    file_path = matching_files[0]
    filename = os.path.basename(file_path)
    file_id = filename.split('_')[0]
    
    print(f"🔍 Testing with file: {filename}")
    print(f"📋 File ID: {file_id}")
    
    # Test the agent status endpoint (assuming backend is running on port 8000)
    try:
        url = f"http://localhost:8000/api/v1/agents/status/{file_id}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check the data agent outputs for filename display
            data_agent_outputs = data.get("agents", {}).get("data-agent", {}).get("outputs", [])
            
            print("\n📊 Data Agent Outputs:")
            for output in data_agent_outputs:
                print(f"  {output}")
                
                # Check if the filename appears correctly (without UUID prefix)
                if "[BACKEND] File:" in output:
                    displayed_filename = output.split("[BACKEND] File: ")[1]
                    expected_filename = "sample_sales_data.csv"
                    
                    if displayed_filename == expected_filename:
                        print(f"✅ Filename display FIXED: '{displayed_filename}'")
                    else:
                        print(f"❌ Filename still shows UUID: '{displayed_filename}'")
            
        else:
            print(f"❌ Backend request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running on port 8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_filename_fix()
