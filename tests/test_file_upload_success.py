#!/usr/bin/env python3
"""
Simple test to check if we can upload a file and index it into Pinecone
"""

import requests
import os
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment
load_dotenv('backend/.env')

def check_pinecone_vectors():
    """Check current vector count"""
    try:
        pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        index = pc.Index('pineindex')
        stats = index.describe_index_stats()
        return stats['total_vector_count']
    except Exception as e:
        print(f"❌ Error checking Pinecone: {e}")
        return None

def test_file_upload_success():
    """Test if file upload creates vectors in Pinecone"""
    
    print("🚀 Testing File Upload → Pinecone Indexing Success")
    print("=" * 60)
    
    # Check vectors BEFORE upload
    vectors_before = check_pinecone_vectors()
    print(f"📊 Vectors BEFORE upload: {vectors_before}")
    
    # Upload file
    print("\n1️⃣ Uploading file...")
    try:
        with open('sample_sales_data.csv', 'rb') as f:
            files = {'file': f}
            response = requests.post('http://localhost:8000/api/v1/upload', files=files, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            file_id = result['file_id']
            print(f"✅ File uploaded: {file_id}")
            
            # Wait a bit for background processing
            import time
            print("⏳ Waiting for background processing...")
            time.sleep(5)
            
            # Check vectors AFTER upload
            vectors_after = check_pinecone_vectors()
            print(f"📊 Vectors AFTER upload: {vectors_after}")
            
            # Check status
            if vectors_after is not None and vectors_before is not None:
                if vectors_after > vectors_before:
                    print("🎉 SUCCESS: File upload created vectors in Pinecone!")
                    print(f"   Added {vectors_after - vectors_before} vectors")
                    return True
                else:
                    print("❌ FAILURE: No vectors were added to Pinecone")
                    print("   File upload pipeline is broken")
                    return False
            else:
                print("❌ ERROR: Cannot check Pinecone status")
                return False
                
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend server not running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

if __name__ == "__main__":
    success = test_file_upload_success()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ File Upload Pipeline: WORKING")
        print("   → Update workflow.txt: File Upload = ✅ SUCCESS")
    else:
        print("❌ File Upload Pipeline: BROKEN") 
        print("   → Keep workflow.txt: File Upload = ❌ FAILURE")
        print("   → Need to debug Data Agent and Retrieval Agent")
