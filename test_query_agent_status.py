#!/usr/bin/env python3
"""
Test Enhanced Query Agent Status
Test the enhanced agent output display during query processing
"""

import requests
import json
import time

def test_query_agent_status():
    """Test enhanced query agent status with real backend outputs"""
    print("🧪 Testing Enhanced Query Agent Status")
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
    
    # Test 2: Test query status with different session IDs
    test_sessions = [
        "query_early_planning",
        "query_12345_processing", 
        "query_67890_sql_active",
        "regular_session_123"
    ]
    
    for session_id in test_sessions:
        print(f"\n📊 Testing session: {session_id}")
        
        try:
            status_response = requests.get(
                f"{backend_url}/api/v1/agents/query-status/{session_id}", 
                timeout=10
            )
            
            if status_response.status_code == 200:
                data = status_response.json()
                print(f"✅ Status: {data.get('status')}")
                print(f"🎯 Current agent: {data.get('current_agent')}")
                
                agents = data.get('agents', {})
                for agent_id, agent_info in agents.items():
                    status = agent_info.get('status', 'unknown')
                    outputs = agent_info.get('outputs', [])
                    
                    if status != 'idle' or outputs:
                        print(f"\n🤖 {agent_id.upper()} - {status.upper()}")
                        for output in outputs:
                            print(f"   - {output}")
                        
                        if status == 'active':
                            print(f"   ⚡ Currently processing...")
                            
            else:
                print(f"❌ Query status failed: {status_response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing session {session_id}: {e}")
    
    # Test 3: Test real-time progression simulation
    print(f"\n📊 Testing real-time progression...")
    
    session_id = f"query_{int(time.time())}_realtime"
    
    for i in range(3):
        print(f"\n⏱️ Status check {i+1}/3:")
        
        try:
            status_response = requests.get(
                f"{backend_url}/api/v1/agents/query-status/{session_id}", 
                timeout=10
            )
            
            if status_response.status_code == 200:
                data = status_response.json()
                current_agent = data.get('current_agent')
                print(f"🎯 Current agent: {current_agent}")
                
                # Show active agent outputs
                agents = data.get('agents', {})
                if current_agent in agents:
                    agent_info = agents[current_agent]
                    outputs = agent_info.get('outputs', [])
                    print(f"📝 {current_agent} outputs:")
                    for output in outputs[-2:]:  # Show last 2 outputs
                        print(f"   - {output}")
                        
            time.sleep(2)  # Wait between status checks
            
        except Exception as e:
            print(f"❌ Error in progression test: {e}")
    
    print("\n✅ Enhanced query agent status test completed!")


if __name__ == "__main__":
    test_query_agent_status()
