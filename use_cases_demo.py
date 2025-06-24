"""
Enterprise Insights Copilot - Three Use Cases Demo
==================================================
This script demonstrates the three core workflows:
1. Upload CSV + SQL Query
2. Upload CSV + Insight Query  
3. Upload CSV + Chart Query
"""

import requests
import json
import time
import os
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"
SAMPLE_CSV = "sample_sales_data.csv"

def check_server_health():
    """Check if both servers are running"""
    try:
        backend_health = requests.get(f"{BACKEND_URL}/api/v1/health").json()
        print("✅ Backend Status:", backend_health)
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Backend server not running!")
        return False

def upload_csv_file(file_path):
    """Upload a CSV file to the backend"""
    print(f"\n📁 Uploading file: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None
    
    with open(file_path, 'rb') as file:
        files = {'file': (os.path.basename(file_path), file, 'text/csv')}
        response = requests.post(f"{BACKEND_URL}/api/v1/upload", files=files)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ File uploaded successfully!")
        print(f"   File ID: {result['file_id']}")
        
        # Debug: print the full response to see what we have
        print(f"   Full response: {result}")
        
        if 'columns' in result:
            print(f"   Columns: {', '.join(result['columns'])}")
        if 'row_count' in result:
            print(f"   Rows: {result['row_count']}")
        
        return result['file_id']
    else:
        print(f"❌ Upload failed: {response.text}")
        return None

def query_data(file_id, query, query_type="general", timeout=60):
    """Send a query to the backend with timeout"""
    print(f"\n💬 Sending {query_type} query: {query}")
    print(f"⏱️ Timeout set to {timeout} seconds")
    
    payload = {
        "query": query,
        "file_id": file_id
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/v1/query", json=payload, timeout=timeout)
        if response.status_code == 200:
            result = response.json()
            print("✅ Query processed successfully!")
            
            # Debug: Show the full query response
            print(f"🔍 DEBUG: Full query response: {json.dumps(result, indent=2)}")
            
            return result
        else:
            print(f"❌ Query failed: {response.text}")
            return None
    except requests.exceptions.Timeout:
        print(f"⏱️ Query timed out after {timeout} seconds!")
        return {"error": "timeout", "message": f"Query processing exceeded {timeout} second timeout"}
    except Exception as e:
        print(f"❌ Error during query: {str(e)}")
        return None

def print_query_result(result, query_type):
    """Print the query result in a formatted way"""
    if not result:
        return
    
    print(f"\n📊 {query_type.upper()} RESULT:")
    print("=" * 60)
    
    # Print the response text
    if 'response' in result:
        print("Response:", result['response'])
    
    # Print any data if available
    if 'data' in result and result['data']:
        print("\nData:")
        for item in result['data'][:5]:  # Show first 5 rows
            print(f"  {item}")
        if len(result['data']) > 5:
            print(f"  ... and {len(result['data']) - 5} more rows")
    
    # Print insights if available
    if 'insights' in result and result['insights']:
        print("\nInsights:")
        for insight in result['insights']:
            print(f"  • {insight}")
    
    # Print visualizations if available
    if 'visualizations' in result and result['visualizations']:
        print("\nVisualizations:")
        for viz in result['visualizations']:
            print(f"  📈 {viz.get('title', 'Chart')}: {viz.get('type', 'Unknown type')}")
    
    print("=" * 60)

def main():
    """Run the three use case demos"""
    print("🚀 Enterprise Insights Copilot - Use Cases Demo")
    print("=" * 60)
    
    # Check server health
    if not check_server_health():
        print("Please start the backend server first!")
        return
    
    # Upload the sample CSV
    file_id = upload_csv_file(SAMPLE_CSV)
    if not file_id:
        print("Failed to upload file. Exiting.")
        return
    
    print(f"\n🎯 Starting three use case demonstrations with file ID: {file_id}")
      # USE CASE 1: SQL Query
    print("\n" + "="*60)
    print("USE CASE 1: SQL QUERY")
    print("="*60)
    
    sql_query = "SELECT category, SUM(sales_amount) as total_sales FROM data GROUP BY category ORDER BY total_sales DESC"
    # Use a 60-second timeout for SQL query
    sql_result = query_data(file_id, sql_query, "SQL", timeout=60)
    
    if sql_result and "error" in sql_result and sql_result["error"] == "timeout":
        print("⏱️ SQL Query timed out. Skipping to next query.")
    else:
        print_query_result(sql_result, "SQL")
    
    time.sleep(2)  # Brief pause between queries
    
    # USE CASE 2: Insight Query
    print("\n" + "="*60)
    print("USE CASE 2: INSIGHT QUERY")
    print("="*60)
    
    insight_query = "What are the key trends and patterns in sales performance across different regions and customer segments?"
    # Use a 60-second timeout for insight query
    insight_result = query_data(file_id, insight_query, "Insight", timeout=60)
    
    if insight_result and "error" in insight_result and insight_result["error"] == "timeout":
        print("⏱️ Insight Query timed out. Skipping to next query.")
    else:
        print_query_result(insight_result, "Insight")
    
    time.sleep(2)  # Brief pause between queries
    
    # USE CASE 3: Chart Query
    print("\n" + "="*60)
    print("USE CASE 3: CHART QUERY")
    print("="*60)
    
    chart_query = "Create a bar chart showing sales by category and a line chart showing sales trends over time"
    # Use a 60-second timeout for chart query
    chart_result = query_data(file_id, chart_query, "Chart", timeout=60)
    
    if chart_result and "error" in chart_result and chart_result["error"] == "timeout":
        print("⏱️ Chart Query timed out. Skipping to next section.")
    else:
        print_query_result(chart_result, "Chart")
    
    # Final summary
    print("\n" + "="*60)
    print("🎉 DEMO COMPLETE!")
    print("="*60)
    print("All three use cases have been demonstrated:")
    print("✅ Use Case 1: SQL Query - Aggregated sales by category")
    print("✅ Use Case 2: Insight Query - Business intelligence analysis")
    print("✅ Use Case 3: Chart Query - Data visualization generation")
    print(f"\n🌐 You can also test these interactively at: {FRONTEND_URL}")
    print("="*60)

if __name__ == "__main__":
    main()
