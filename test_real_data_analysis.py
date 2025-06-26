#!/usr/bin/env python3
"""
Test script to analyze the uploaded heart surgery data and show real agent outputs
"""

import requests
import json
import os
import glob

def test_real_data_analysis():
    """Test real data analysis from uploaded files"""
    
    print("🔍 Looking for uploaded files...")
    
    # Find uploaded files
    upload_dir = "backend/uploads" if os.path.exists("backend/uploads") else "uploads"
    if os.path.exists(upload_dir):
        files = os.listdir(upload_dir)
        print(f"Found files in {upload_dir}: {files}")
        
        if files:
            # Get the most recent file
            latest_file = files[-1]
            file_id = latest_file.split('_')[0] if '_' in latest_file else latest_file.split('.')[0]
            
            print(f"\n📊 Testing agent status for file: {latest_file}")
            print(f"📊 Using file ID: {file_id}")
            
            # Test the agent status endpoint
            try:
                response = requests.get(f"http://localhost:8000/api/v1/agents/status/{file_id}")
                if response.status_code == 200:
                    data = response.json()
                    print("\n🎉 Real agent analysis:")
                    print(json.dumps(data, indent=2))
                    
                    print("\n📋 Data Agent Outputs:")
                    for output in data.get('agents', {}).get('data-agent', {}).get('outputs', []):
                        print(f"  • {output}")
                    
                    print("\n🔍 Retrieval Agent Outputs:")
                    for output in data.get('agents', {}).get('retrieval-agent', {}).get('outputs', []):
                        print(f"  • {output}")
                        
                else:
                    print(f"❌ Agent status failed: {response.status_code}")
                    print(f"Error: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error testing agent status: {e}")
        else:
            print("❌ No uploaded files found")
    else:
        print(f"❌ Upload directory not found: {upload_dir}")

def analyze_local_data():
    """Analyze the heart surgery data directly"""
    print("\n🩺 Direct analysis of heart surgery data:")
    
    upload_dirs = ["backend/uploads", "uploads"]
    
    for upload_dir in upload_dirs:
        if os.path.exists(upload_dir):
            csv_files = [f for f in os.listdir(upload_dir) if f.endswith('.csv')]
            
            for file in csv_files:
                if 'heart' in file.lower() or 'surgery' in file.lower():
                    file_path = os.path.join(upload_dir, file)
                    print(f"\n📁 Analyzing: {file}")
                    
                    try:
                        import pandas as pd
                        df = pd.read_csv(file_path)
                        
                        print(f"📊 Shape: {df.shape}")
                        print(f"📊 Columns: {list(df.columns)}")
                        print(f"📊 Data types:\n{df.dtypes}")
                        print(f"📊 Sample data:\n{df.head()}")
                        print(f"📊 Missing values:\n{df.isnull().sum()}")
                        
                    except Exception as e:
                        print(f"❌ Error analyzing {file}: {e}")
                        
            break

if __name__ == "__main__":
    test_real_data_analysis()
    analyze_local_data()
