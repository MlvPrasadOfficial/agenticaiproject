"""
Simple Three Use Cases Demo
==========================
Demonstrates the three core workflows of Enterprise Insights Copilot
"""

import requests
import json
import time
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

BACKEND_URL = "http://localhost:8000"

def check_backend():
    """Check if backend is running"""
    print("🔍 DEBUG: Starting backend connectivity check...")
    try:
        print(f"🔍 DEBUG: Attempting to connect to {BACKEND_URL}/")
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        print(f"🔍 DEBUG: Response status code: {response.status_code}")
        print(f"🔍 DEBUG: Response headers: {dict(response.headers)}")
        print(f"🔍 DEBUG: Response content: {response.text}")
        
        if response.status_code == 200:
            print("✅ DEBUG: Backend root endpoint responded successfully")
            return True
        else:
            print(f"❌ DEBUG: Backend returned status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ DEBUG: Failed to connect to backend: {type(e).__name__}: {e}")
        return False

def upload_file(file_path):
    """Upload CSV file to backend"""
    print(f"🔍 DEBUG: Starting file upload for {file_path}")
    print(f"🔍 DEBUG: File exists: {file_path.exists()}")
    print(f"🔍 DEBUG: File size: {file_path.stat().st_size if file_path.exists() else 'N/A'} bytes")
    
    try:
        with open(file_path, 'rb') as file:
            files = {'file': (file_path.name, file, 'text/csv')}
            upload_url = f"{BACKEND_URL}/api/v1/upload"
            print(f"🔍 DEBUG: Uploading to {upload_url}")
            
            response = requests.post(upload_url, files=files, timeout=30)
            print(f"🔍 DEBUG: Upload response status: {response.status_code}")
            print(f"🔍 DEBUG: Upload response headers: {dict(response.headers)}")
            print(f"🔍 DEBUG: Upload response content: {response.text}")
    
        if response.status_code == 200:
            result = response.json()
            print(f"✅ DEBUG: Upload successful, file_id: {result.get('file_id', 'Unknown')}")
            return result['file_id']
        else:
            print(f"❌ DEBUG: Upload failed with status {response.status_code}")
            raise RuntimeError(f"Upload failed: {response.text}")
            
    except Exception as e:
        print(f"❌ DEBUG: Upload exception: {type(e).__name__}: {e}")
        raise

def send_query(file_id, query):
    """Send query to backend"""
    print(f"🔍 DEBUG: Sending query with file_id: {file_id}")
    print(f"🔍 DEBUG: Query: {query[:100]}{'...' if len(query) > 100 else ''}")
    
    try:
        payload = {"query": query, "file_id": file_id}
        query_url = f"{BACKEND_URL}/api/v1/query"
        print(f"🔍 DEBUG: Posting to {query_url}")
        print(f"🔍 DEBUG: Payload: {payload}")
        response = requests.post(query_url, json=payload, timeout=60)
        print(f"🔍 DEBUG: Query response status: {response.status_code}")
        print(f"🔍 DEBUG: Query response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ DEBUG: Query successful, response keys: {list(result.keys())}")
            
            # Show actual response content
            if 'result' in result:
                print(f"🔍 DEBUG: Result content: {result['result']}")
            if 'response' in result:
                print(f"🔍 DEBUG: Response content: {result['response']}")
            if 'data' in result:
                print(f"🔍 DEBUG: Data content: {result['data']}")
            if 'insights' in result:
                print(f"🔍 DEBUG: Insights: {result['insights']}")
            if 'visualizations' in result:
                print(f"🔍 DEBUG: Visualizations: {result['visualizations']}")
            if 'agent_trace' in result:
                print(f"🔍 DEBUG: Agent trace: {result['agent_trace']}")
                
            return result
        else:
            print(f"❌ DEBUG: Query failed with status {response.status_code}")
            print(f"❌ DEBUG: Query error response: {response.text}")
            raise RuntimeError(f"Query failed: {response.text}")
            
    except Exception as e:
        print(f"❌ DEBUG: Query exception: {type(e).__name__}: {e}")
        raise

def main():
    """Run the three use case demonstrations"""
    print("🚀 Enterprise Insights Copilot - Three Use Cases Demo")
    print("=" * 60)
      # Check backend
    if not check_backend():
        print("❌ Backend server not running!")
        print("💡 Please start it with: conda activate munna; cd backend; python main.py")
        return
    
    print("✅ Backend server is running")
    
    # Use the existing sample CSV
    csv_file = Path("sample_sales_data.csv")
    print(f"🔍 DEBUG: Looking for CSV file at: {csv_file.absolute()}")
    print(f"🔍 DEBUG: Current working directory: {Path.cwd()}")
    print(f"🔍 DEBUG: Files in current directory: {list(Path.cwd().glob('*.csv'))}")
    
    if not csv_file.exists():
        print("❌ Sample CSV file not found in current directory!")
        # Try to find it in parent directory
        parent_csv = Path("../sample_sales_data.csv")
        print(f"🔍 DEBUG: Trying parent directory: {parent_csv.absolute()}")
        if parent_csv.exists():
            csv_file = parent_csv
            print("✅ Found CSV file in parent directory")
        else:
            print("❌ Sample CSV file not found in parent directory either!")
            return
    
    # Upload file
    print(f"\n📁 Uploading file: {csv_file}")
    try:
        file_id = upload_file(csv_file)
        print(f"✅ File uploaded successfully! ID: {file_id}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return
    
    # USE CASE 1: SQL Query
    print("\n" + "="*60)
    print("USE CASE 1: SQL QUERY")
    print("="*60)
    
    sql_query = "SELECT category, SUM(sales_amount) as total_sales FROM data GROUP BY category ORDER BY total_sales DESC"
    print(f"Query: {sql_query}")
    
    try:
        result1 = send_query(file_id, sql_query)
        print("✅ SQL query successful!")
        if 'response' in result1:
            print(f"Response: {result1['response'][:200]}...")
    except Exception as e:
        print(f"❌ SQL query failed: {e}")
    
    time.sleep(2)
    
    # USE CASE 2: Insight Query
    print("\n" + "="*60)
    print("USE CASE 2: INSIGHT QUERY")
    print("="*60)
    
    insight_query = "What are the key trends and patterns in sales performance across different regions and customer segments?"
    print(f"Query: {insight_query}")
    
    try:
        result2 = send_query(file_id, insight_query)
        print("✅ Insight query successful!")
        if 'response' in result2:
            print(f"Response: {result2['response'][:200]}...")
        if 'insights' in result2 and result2['insights']:
            print(f"Generated {len(result2['insights'])} insights")
    except Exception as e:
        print(f"❌ Insight query failed: {e}")
    
    time.sleep(2)
    
    # USE CASE 3: Chart Query
    print("\n" + "="*60)
    print("USE CASE 3: CHART QUERY")
    print("="*60)
    
    chart_query = "Create a bar chart showing sales by category and a line chart showing sales trends over time"
    print(f"Query: {chart_query}")
    
    try:
        result3 = send_query(file_id, chart_query)
        print("✅ Chart query successful!")
        if 'response' in result3:
            print(f"Response: {result3['response'][:200]}...")
        if 'visualizations' in result3 and result3['visualizations']:
            print(f"Generated {len(result3['visualizations'])} visualizations")
            for i, viz in enumerate(result3['visualizations'], 1):
                print(f"  📊 Chart {i}: {viz.get('title', 'Untitled')} ({viz.get('type', 'unknown')})")
    except Exception as e:
        print(f"❌ Chart query failed: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("🎉 DEMO COMPLETE!")
    print("="*60)
    print("Three use cases demonstrated:")
    print("✅ Use Case 1: SQL Query - Direct data querying")
    print("✅ Use Case 2: Insight Query - Business intelligence analysis")
    print("✅ Use Case 3: Chart Query - Data visualization generation")
    print("\n🌐 You can also test these interactively at: http://localhost:3000")

if __name__ == "__main__":
    main()
