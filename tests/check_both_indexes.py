#!/usr/bin/env python3

import sys
import os

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_path)

from pinecone import Pinecone

def check_both_indexes():
    """Check both Pinecone indexes"""
    
    print("🚀 Pinecone Indexes Comparison")
    print("=" * 50)
    
    try:
        # Read API key from environment or settings
        api_key = os.getenv('PINECONE_API_KEY')
        if not api_key:
            print("❌ PINECONE_API_KEY not found in environment")
            return
            
        # Initialize Pinecone
        pc = Pinecone(api_key=api_key)
        
        # Check both indexes
        indexes_to_check = ["pineindex", "enterprise-insights-384"]
        
        for index_name in indexes_to_check:
            print(f"\n📊 Index '{index_name}':")
            try:
                index = pc.Index(index_name)
                stats = index.describe_index_stats()
                
                print(f"   Dimension: {stats.get('dimension', 'unknown')}")
                print(f"   Total vectors: {stats.get('total_vector_count', 0)}")
                
                # Check namespaces
                namespaces = stats.get('namespaces', {})
                if namespaces:
                    print(f"   Namespaces: {list(namespaces.keys())}")
                    for ns, ns_stats in namespaces.items():
                        print(f"     - {ns}: {ns_stats.get('vector_count', 0)} vectors")
                else:
                    print("   No vectors found")
                    
            except Exception as e:
                print(f"   ❌ Error accessing index: {e}")
                
    except Exception as e:
        print(f"❌ Error checking Pinecone: {e}")

if __name__ == "__main__":
    check_both_indexes()
