#!/usr/bin/env python3
"""Test uploading data to Pinecone"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from dotenv import load_dotenv
import pandas as pd
import uuid
from sentence_transformers import SentenceTransformer
import time

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

def test_pinecone_upload():
    """Test uploading a sample document to Pinecone"""
    try:
        api_key = os.getenv('PINECONE_API_KEY')
        environment = os.getenv('PINECONE_ENVIRONMENT', 'us-east-1-aws')
        target_index = os.getenv('PINECONE_INDEX_NAME', 'pineindex')
        
        if not api_key:
            print("❌ No PINECONE_API_KEY found in environment")
            return False
            
        print(f"🔍 Testing with API key: {api_key[:20]}...")
        print(f"🔍 Environment: {environment}")
        print(f"🔍 Target index name: {target_index}")
        
        # Load sample data
        try:
            csv_path = "../sample_sales_data.csv"
            df = pd.read_csv(csv_path)
            print(f"📊 Loaded sample data: {df.shape[0]} rows, {df.columns.tolist()}")
            
            # Take first 5 rows to create sample documents
            sample_data = df.head(5)
        except Exception as e:
            print(f"❌ Error loading sample data: {e}")
            return False
        
        # Initialize embedding model
        print("🧠 Initializing embedding model...")
        try:
            model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Embedding model loaded")
        except Exception as e:
            print(f"❌ Error loading embedding model: {e}")
            return False
        
        # Try with both Pinecone client versions
        success = False
        
        # Try new Pinecone client (v3+)
        try:
            from pinecone import Pinecone
            print("\n=== Using new Pinecone Python client (v3+) ===")
            
            # Initialize Pinecone
            pc = Pinecone(api_key=api_key)
            print("✅ Pinecone v3+ client initialized")
            
            # Check if index exists
            indexes = pc.list_indexes()
            index_names = [idx.name for idx in indexes]
            
            if target_index in index_names:
                index = pc.Index(target_index)
                
                # Create documents and embeddings
                records = []
                print("🔢 Generating embeddings for sample data...")
                
                for i, row in sample_data.iterrows():
                    # Create a text representation of the row
                    text = f"Product: {row['product']} | Category: {row['category']} | Sales: ${row['sales_amount']}"
                    
                    # Generate embedding
                    vector = model.encode(text).tolist()
                    
                    # Create record
                    record_id = f"test_{int(time.time())}_{i}"
                    records.append({
                        "id": record_id,
                        "values": vector,
                        "metadata": {
                            "product": row['product'],
                            "category": row['category'],
                            "sales": float(row['sales_amount']),
                            "text": text
                        }
                    })
                
                # Upsert records
                print(f"📤 Uploading {len(records)} records to Pinecone...")
                result = index.upsert(vectors=records, namespace="test_namespace")
                print(f"✅ Upload result: {result}")
                
                # Search with one of the vectors
                print("\n🔍 Testing vector search...")
                query_vector = model.encode("Electronics sales").tolist()
                search_results = index.query(
                    vector=query_vector,
                    top_k=3,
                    include_metadata=True,
                    namespace="test_namespace"
                )
                print("📊 Search results:")
                print(search_results)
                
                # Delete test records to clean up
                print("\n🧹 Cleaning up test data...")
                ids_to_delete = [r["id"] for r in records]
                index.delete(ids=ids_to_delete, namespace="test_namespace")
                print("✅ Test data deleted")
                
                success = True
            else:
                print(f"⚠️ Target index '{target_index}' not found")
                
        except ImportError:
            print("⚠️ New Pinecone client not available")
        except Exception as e:
            print(f"❌ Error with new Pinecone client: {e}")
        
        # Try legacy Pinecone client if the new one failed
        if not success:
            try:
                import pinecone
                print("\n=== Using legacy Pinecone client (v2) ===")
                
                # Initialize Pinecone
                pinecone.init(api_key=api_key, environment=environment)
                print("✅ Legacy Pinecone client initialized")
                
                # Check if index exists
                indexes = pinecone.list_indexes()
                
                if target_index in indexes:
                    index = pinecone.Index(target_index)
                    
                    # Create documents and embeddings
                    records = []
                    print("🔢 Generating embeddings for sample data...")
                    
                    for i, row in sample_data.iterrows():
                        # Create a text representation of the row
                        text = f"Product: {row['product']} | Category: {row['category']} | Sales: ${row['sales_amount']}"
                        
                        # Generate embedding
                        vector = model.encode(text).tolist()
                        
                        # Create record
                        record_id = f"test_{int(time.time())}_{i}"
                        records.append(
                            (record_id, vector, {
                                "product": row['product'],
                                "category": row['category'],
                                "sales": float(row['sales_amount']),
                                "text": text
                            })
                        )
                    
                    # Upsert records
                    print(f"📤 Uploading {len(records)} records to Pinecone...")
                    upsert_response = index.upsert(
                        vectors=records,
                        namespace="test_namespace"
                    )
                    print(f"✅ Upload result: {upsert_response}")
                    
                    # Search with one of the vectors
                    print("\n🔍 Testing vector search...")
                    query_vector = model.encode("Electronics sales").tolist()
                    search_results = index.query(
                        vector=query_vector,
                        top_k=3,
                        include_metadata=True,
                        namespace="test_namespace"
                    )
                    print("📊 Search results:")
                    print(search_results)
                    
                    # Delete test records to clean up
                    print("\n🧹 Cleaning up test data...")
                    ids_to_delete = [r[0] for r in records]
                    index.delete(ids=ids_to_delete, namespace="test_namespace")
                    print("✅ Test data deleted")
                    
                    success = True
                else:
                    print(f"⚠️ Target index '{target_index}' not found")
                    
            except ImportError:
                print("⚠️ Legacy Pinecone client not available")
            except Exception as e:
                print(f"❌ Error with legacy Pinecone client: {e}")
        
        return success
        
    except Exception as e:
        print(f"❌ Pinecone upload test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n=== PINECONE UPLOAD TEST ===")
    success = test_pinecone_upload()
    
    if success:
        print("\n✅ Pinecone upload test completed successfully!")
    else:
        print("\n❌ Pinecone upload test failed!")
