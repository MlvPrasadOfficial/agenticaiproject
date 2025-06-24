#!/usr/bin/env python3
"""
Integration Test Suite for Enterprise Insights Copilot
Tests end-to-end functionality of the complete system
"""

import asyncio
import aiohttp
import json
import sys
import time
from pathlib import Path


async def test_backend_health():
    """Test backend health endpoint"""
    print("🔍 Testing backend health...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("http://localhost:8000/api/v1/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Backend healthy: {data['status']}")
                    return True
                else:
                    print(f"❌ Backend health check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Backend connection failed: {e}")
            return False


async def test_file_upload():
    """Test file upload functionality"""
    print("🔍 Testing file upload...")
    
    # Create a sample CSV file for testing
    test_csv_content = """name,age,salary,department
John Doe,30,50000,Engineering
Jane Smith,25,45000,Marketing
Bob Johnson,35,60000,Engineering
Alice Brown,28,48000,Sales
Charlie Wilson,32,55000,Marketing"""
    
    test_file_path = Path("test_data.csv")
    test_file_path.write_text(test_csv_content)
    
    async with aiohttp.ClientSession() as session:
        try:
            data = aiohttp.FormData()
            data.add_field('file', 
                         open(test_file_path, 'rb'),
                         filename='test_data.csv',
                         content_type='text/csv')
            
            async with session.post("http://localhost:8000/api/v1/upload", data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ File upload successful: {result['filename']}")
                    return result['file_id']
                else:
                    text = await response.text()
                    print(f"❌ File upload failed: {response.status} - {text}")
                    return None
        except Exception as e:
            print(f"❌ File upload error: {e}")
            return None
        finally:
            # Clean up test file
            if test_file_path.exists():
                test_file_path.unlink()


async def test_query_processing(file_id: str):
    """Test query processing with uploaded file"""
    print("🔍 Testing query processing...")
    
    query_request = {
        "query": "What is the average salary by department?",
        "file_context": {"file_id": file_id},
        "query_type": "analytical",
        "timestamp": int(time.time())
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                "http://localhost:8000/api/v1/query",
                json=query_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Query processing successful")
                    print(f"   Session ID: {result.get('session_id', 'N/A')}")
                    print(f"   Insights: {len(result.get('results', {}).get('insights', []))}")
                    print(f"   Visualizations: {len(result.get('results', {}).get('visualizations', []))}")
                    return result.get('session_id')
                else:
                    text = await response.text()
                    print(f"❌ Query processing failed: {response.status} - {text}")
                    return None
        except Exception as e:
            print(f"❌ Query processing error: {e}")
            return None


async def test_frontend_accessibility():
    """Test frontend accessibility"""
    print("🔍 Testing frontend accessibility...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("http://localhost:3000") as response:
                if response.status == 200:
                    print("✅ Frontend accessible")
                    return True
                else:
                    print(f"❌ Frontend not accessible: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Frontend connection failed: {e}")
            return False


async def run_integration_tests():
    """Run all integration tests"""
    print("🚀 Starting Enterprise Insights Copilot Integration Tests")
    print("=" * 60)
    
    success_count = 0
    total_tests = 4
    
    # Test 1: Backend Health
    if await test_backend_health():
        success_count += 1
    
    # Test 2: Frontend Accessibility  
    if await test_frontend_accessibility():
        success_count += 1
    
    # Test 3: File Upload
    file_id = await test_file_upload()
    if file_id:
        success_count += 1
        
        # Test 4: Query Processing (depends on file upload)
        session_id = await test_query_processing(file_id)
        if session_id:
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"🎯 Integration Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed! System is fully operational.")
        return True
    else:
        print("⚠️  Some tests failed. Check the logs above.")
        return False


if __name__ == "__main__":
    # Run the integration tests
    success = asyncio.run(run_integration_tests())
    sys.exit(0 if success else 1)
