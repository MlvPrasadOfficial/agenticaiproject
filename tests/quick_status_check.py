#!/usr/bin/env python3
"""
Quick status check for file upload and Pinecone integration
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load environment from backend
load_dotenv('backend/.env')

def check_file_upload():
    """Test if file upload works"""
    print("🔍 Testing file upload...")
    
    # Check if sample file exists
    sample_files = [
        "../sample_sales_data.csv",
        "sample_sales_data.csv", 
        "../backend/sample_sales_data.csv"
    ]
    
    sample_file = None
    for file_path in sample_files:
        if os.path.exists(file_path):
            sample_file = file_path
            break
    
    if not sample_file:
        print("❌ No sample file found")
        return False
    
    print(f"✅ Sample file found: {sample_file}")
    
    # Try to upload to backend
    try:
        url = "http://localhost:8000/api/v1/upload"
        
        with open(sample_file, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ File upload successful: {result}")
            return True
        else:
            print(f"❌ File upload failed: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend server not running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ File upload error: {e}")
        return False

def check_pinecone_config():
    """Test Pinecone configuration"""
    print("\n🔍 Testing Pinecone configuration...")
    
    api_key = os.getenv('PINECONE_API_KEY')
    if not api_key:
        print("❌ PINECONE_API_KEY not found in environment")
        return False
    
    print(f"✅ PINECONE_API_KEY found: {api_key[:10]}...")
    
    try:
        from pinecone import Pinecone
        
        pc = Pinecone(api_key=api_key)
        indexes = pc.list_indexes()
        print(f"✅ Pinecone connection successful")
        print(f"📊 Available indexes: {[idx.name for idx in indexes]}")
        
        # Check specific index
        index_name = os.getenv('PINECONE_INDEX_NAME', 'pineindex')
        index_names = [idx.name for idx in indexes]
        
        if index_name in index_names:
            print(f"✅ Target index '{index_name}' exists")
            index = pc.Index(index_name)
            stats = index.describe_index_stats()
            print(f"📊 Index stats: {stats}")
            return True
        else:
            print(f"❌ Target index '{index_name}' not found in {index_names}")
            return False
            
    except Exception as e:
        print(f"❌ Pinecone error: {e}")
        return False

def check_agents():
    """Check which agents are implemented"""
    print("\n🔍 Checking agent implementations...")
    
    agents_dir = "backend/app/agents"
    if not os.path.exists(agents_dir):
        print("❌ Agents directory not found")
        return {}
    
    agents = {}
    for filename in os.listdir(agents_dir):
        if filename.endswith('_agent.py') and not filename.startswith('__'):
            agent_name = filename.replace('_agent.py', '')
            agents[agent_name] = os.path.exists(os.path.join(agents_dir, filename))
    
    print("📋 Agent Status:")
    for agent, exists in agents.items():
        status = "✅ EXISTS" if exists else "❌ MISSING"
        print(f"  {agent}: {status}")
    
    # Check for expected agents
    expected_agents = ['data', 'retrieval', 'planning', 'query', 'sql', 'insight', 'chart', 'report', 'critique', 'debate', 'narrative']
    missing_agents = []
    
    for expected in expected_agents:
        if expected not in agents:
            missing_agents.append(expected)
    
    if missing_agents:
        print(f"❌ Missing agents: {missing_agents}")
    else:
        print("✅ All expected agents found")
    
    return agents

def main():
    """Run all status checks"""
    print("🚀 Quick Status Check for Enterprise Insights Copilot")
    print("=" * 60)
    
    # Check components
    file_upload_ok = check_file_upload()
    pinecone_ok = check_pinecone_config()
    agents = check_agents()
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY:")
    print(f"  File Upload: {'✅ WORKING' if file_upload_ok else '❌ FAILED'}")
    print(f"  Pinecone: {'✅ WORKING' if pinecone_ok else '❌ FAILED'}")
    print(f"  Agents: {len(agents)} implemented")
    
    if file_upload_ok and pinecone_ok:
        print("🎉 Core systems operational!")
    else:
        print("⚠️ Issues found - check logs above")

if __name__ == "__main__":
    main()
