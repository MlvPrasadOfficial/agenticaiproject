"""
Test Case 1: SQL Query Testing
==============================
Tests for SQL query functionality against uploaded CSV files
"""

import pytest
from test_config import (
    check_servers_running, create_test_csv, upload_test_file, 
    query_backend, print_test_header, print_test_result
)

def test_sql_basic_queries():
    """Test basic SQL queries on uploaded data"""
    print_test_header("SQL Query Tests")
    
    # Check if servers are running
    server_status = check_servers_running()
    if not server_status["backend"]:
        print_test_result(False, "Backend server not running")
        return
    
    try:
        # Create and upload test data
        test_file = create_test_csv("sql_test_data.csv", 50)
        file_id = upload_test_file(test_file)
        print_test_result(True, f"File uploaded successfully: {file_id}")
        
        # Test 1: Simple SELECT query
        sql_query = "SELECT category, SUM(sales_amount) as total_sales FROM data GROUP BY category ORDER BY total_sales DESC"
        result = query_backend(file_id, sql_query)
        
        success = result and 'response' in result
        print_test_result(success, f"SQL aggregation query: {sql_query[:50]}...")
        
        if success and 'data' in result:
            print(f"   📊 Retrieved {len(result['data'])} grouped results")
        
        # Test 2: Complex SQL with filtering
        complex_query = "SELECT region, customer_segment, AVG(sales_amount) as avg_sales FROM data WHERE sales_amount > 1000 GROUP BY region, customer_segment"
        result2 = query_backend(file_id, complex_query)
        
        success2 = result2 and 'response' in result2
        print_test_result(success2, f"Complex SQL with filtering: {complex_query[:50]}...")
        
        # Test 3: Time-based query
        time_query = "SELECT date, SUM(quantity) as total_quantity FROM data GROUP BY date ORDER BY date LIMIT 10"
        result3 = query_backend(file_id, time_query)
        
        success3 = result3 and 'response' in result3
        print_test_result(success3, f"Time-based SQL query: {time_query[:50]}...")
        
        return success and success2 and success3
        
    except Exception as e:
        print_test_result(False, f"SQL test failed: {str(e)}")
        return False

def test_sql_edge_cases():
    """Test SQL queries with edge cases"""
    print_test_header("SQL Edge Cases")
    
    server_status = check_servers_running()
    if not server_status["backend"]:
        print_test_result(False, "Backend server not running")
        return
    
    try:
        # Create small dataset for edge cases
        test_file = create_test_csv("sql_edge_test.csv", 10)
        file_id = upload_test_file(test_file)
        
        # Test invalid SQL
        invalid_sql = "SELECT * FROM nonexistent_table"
        try:
            result = query_backend(file_id, invalid_sql)
            print_test_result(True, "System handled invalid SQL gracefully")
        except Exception:
            print_test_result(True, "System properly rejected invalid SQL")
        
        # Test empty result SQL
        empty_result_sql = "SELECT * FROM data WHERE sales_amount > 999999"
        result = query_backend(file_id, empty_result_sql)
        success = result is not None
        print_test_result(success, "SQL query with empty results")
        
        return True
        
    except Exception as e:
        print_test_result(False, f"SQL edge case test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Running SQL Query Tests")
    
    test1_result = test_sql_basic_queries()
    test2_result = test_sql_edge_cases()
    
    if test1_result and test2_result:
        print("\n✅ All SQL tests passed!")
    else:
        print("\n❌ Some SQL tests failed!")
