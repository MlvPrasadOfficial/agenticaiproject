"""
Test Case 2: Insight Query Testing
=================================
Tests for business intelligence and insight generation
"""

import pytest
from test_config import (
    check_servers_running, create_test_csv, upload_test_file, 
    query_backend, print_test_header, print_test_result
)

def test_insight_generation():
    """Test business insight generation from data"""
    print_test_header("Insight Generation Tests")
    
    # Check if servers are running
    server_status = check_servers_running()
    if not server_status["backend"]:
        print_test_result(False, "Backend server not running")
        return
    
    try:
        # Create and upload test data
        test_file = create_test_csv("insight_test_data.csv", 100)
        file_id = upload_test_file(test_file)
        print_test_result(True, f"File uploaded successfully: {file_id}")
        
        # Test 1: General business insights
        insight_query = "What are the key trends and patterns in sales performance across different regions and customer segments?"
        result = query_backend(file_id, insight_query)
        
        success = result and 'response' in result
        print_test_result(success, "General business insights query")
        
        if success:
            print(f"   💡 Generated insight response: {len(result.get('response', ''))} characters")
            if 'insights' in result and result['insights']:
                print(f"   📈 Found {len(result['insights'])} specific insights")
        
        # Test 2: Performance analysis
        performance_query = "Analyze the performance of different product categories and identify top performers"
        result2 = query_backend(file_id, performance_query)
        
        success2 = result2 and 'response' in result2
        print_test_result(success2, "Product performance analysis")
        
        # Test 3: Customer segmentation insights
        segment_query = "What insights can you provide about customer behavior patterns and segmentation?"
        result3 = query_backend(file_id, segment_query)
        
        success3 = result3 and 'response' in result3
        print_test_result(success3, "Customer segmentation insights")
        
        return success and success2 and success3
        
    except Exception as e:
        print_test_result(False, f"Insight test failed: {str(e)}")
        return False

def test_trend_analysis():
    """Test trend and pattern analysis capabilities"""
    print_test_header("Trend Analysis Tests")
    
    server_status = check_servers_running()
    if not server_status["backend"]:
        print_test_result(False, "Backend server not running")
        return
    
    try:
        # Create time-series heavy dataset
        test_file = create_test_csv("trend_test_data.csv", 200)
        file_id = upload_test_file(test_file)
        
        # Test trend analysis
        trend_query = "Identify sales trends over time and seasonal patterns in the data"
        result = query_backend(file_id, trend_query)
        
        success = result and 'response' in result
        print_test_result(success, "Time-series trend analysis")
        
        # Test correlation analysis
        correlation_query = "Find correlations between different variables and explain their business significance"
        result2 = query_backend(file_id, correlation_query)
        
        success2 = result2 and 'response' in result2
        print_test_result(success2, "Correlation analysis")
        
        return success and success2
        
    except Exception as e:
        print_test_result(False, f"Trend analysis test failed: {str(e)}")
        return False

def test_anomaly_detection():
    """Test anomaly and outlier detection"""
    print_test_header("Anomaly Detection Tests")
    
    server_status = check_servers_running()
    if not server_status["backend"]:
        print_test_result(False, "Backend server not running")
        return
    
    try:
        test_file = create_test_csv("anomaly_test_data.csv", 75)
        file_id = upload_test_file(test_file)
        
        # Test anomaly detection
        anomaly_query = "Detect any anomalies, outliers, or unusual patterns in the sales data"
        result = query_backend(file_id, anomaly_query)
        
        success = result and 'response' in result
        print_test_result(success, "Anomaly detection analysis")
        
        return success
        
    except Exception as e:
        print_test_result(False, f"Anomaly detection test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Running Insight Query Tests")
    
    test1_result = test_insight_generation()
    test2_result = test_trend_analysis()
    test3_result = test_anomaly_detection()
    
    if test1_result and test2_result and test3_result:
        print("\n✅ All insight tests passed!")
    else:
        print("\n❌ Some insight tests failed!")
