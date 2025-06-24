"""
Test Case 3: Chart Query Testing
===============================
Tests for data visualization and chart generation
"""

import pytest
from test_config import (
    check_servers_running, create_test_csv, upload_test_file, 
    query_backend, print_test_header, print_test_result
)

def test_chart_generation():
    """Test chart and visualization generation"""
    print_test_header("Chart Generation Tests")
    
    # Check if servers are running
    server_status = check_servers_running()
    if not server_status["backend"]:
        print_test_result(False, "Backend server not running")
        return
    
    try:
        # Create and upload test data
        test_file = create_test_csv("chart_test_data.csv", 80)
        file_id = upload_test_file(test_file)
        print_test_result(True, f"File uploaded successfully: {file_id}")
        
        # Test 1: Bar chart generation
        bar_chart_query = "Create a bar chart showing sales by category"
        result = query_backend(file_id, bar_chart_query)
        
        success = result and 'response' in result
        print_test_result(success, "Bar chart generation")
        
        if success and 'visualizations' in result:
            charts = result['visualizations']
            print(f"   📊 Generated {len(charts)} visualization(s)")
            for chart in charts:
                chart_type = chart.get('type', 'unknown')
                chart_title = chart.get('title', 'Untitled')
                print(f"     • {chart_type}: {chart_title}")
        
        # Test 2: Line chart generation
        line_chart_query = "Create a line chart showing sales trends over time"
        result2 = query_backend(file_id, line_chart_query)
        
        success2 = result2 and 'response' in result2
        print_test_result(success2, "Line chart generation")
        
        # Test 3: Multiple chart types
        multi_chart_query = "Create multiple charts: a pie chart for category distribution, a scatter plot for sales vs quantity, and a histogram for sales amount distribution"
        result3 = query_backend(file_id, multi_chart_query)
        
        success3 = result3 and 'response' in result3
        print_test_result(success3, "Multiple chart generation")
        
        if success3 and 'visualizations' in result3:
            charts = result3['visualizations']
            print(f"   📊 Generated {len(charts)} chart(s) from multi-chart request")
        
        return success and success2 and success3
        
    except Exception as e:
        print_test_result(False, f"Chart generation test failed: {str(e)}")
        return False

def test_dashboard_creation():
    """Test dashboard and complex visualization creation"""
    print_test_header("Dashboard Creation Tests")
    
    server_status = check_servers_running()
    if not server_status["backend"]:
        print_test_result(False, "Backend server not running")
        return
    
    try:
        test_file = create_test_csv("dashboard_test_data.csv", 120)
        file_id = upload_test_file(test_file)
        
        # Test dashboard creation
        dashboard_query = "Create a comprehensive dashboard with multiple visualizations showing sales performance, regional analysis, and customer insights"
        result = query_backend(file_id, dashboard_query)
        
        success = result and 'response' in result
        print_test_result(success, "Comprehensive dashboard creation")
        
        if success and 'visualizations' in result:
            charts = result['visualizations']
            print(f"   📈 Dashboard contains {len(charts)} visualization(s)")
        
        return success
        
    except Exception as e:
        print_test_result(False, f"Dashboard creation test failed: {str(e)}")
        return False

def test_chart_customization():
    """Test chart customization and styling options"""
    print_test_header("Chart Customization Tests")
    
    server_status = check_servers_running()
    if not server_status["backend"]:
        print_test_result(False, "Backend server not running")
        return
    
    try:
        test_file = create_test_csv("custom_chart_test.csv", 60)
        file_id = upload_test_file(test_file)
        
        # Test custom styling
        custom_query = "Create a professional-looking bar chart with custom colors showing sales by region, include proper labels and title"
        result = query_backend(file_id, custom_query)
        
        success = result and 'response' in result
        print_test_result(success, "Custom chart styling")
        
        # Test interactive features
        interactive_query = "Create an interactive chart that allows users to explore sales data by different dimensions"
        result2 = query_backend(file_id, interactive_query)
        
        success2 = result2 and 'response' in result2
        print_test_result(success2, "Interactive chart creation")
        
        return success and success2
        
    except Exception as e:
        print_test_result(False, f"Chart customization test failed: {str(e)}")
        return False

def test_chart_edge_cases():
    """Test chart generation with edge cases"""
    print_test_header("Chart Edge Cases")
    
    server_status = check_servers_running()
    if not server_status["backend"]:
        print_test_result(False, "Backend server not running")
        return
    
    try:
        # Small dataset
        test_file = create_test_csv("small_chart_test.csv", 5)
        file_id = upload_test_file(test_file)
        
        # Test with minimal data
        minimal_query = "Create charts from this small dataset"
        result = query_backend(file_id, minimal_query)
        
        success = result and 'response' in result
        print_test_result(success, "Chart generation with minimal data")
        
        # Test invalid chart request
        invalid_query = "Create a chart showing correlation between text fields"
        result2 = query_backend(file_id, invalid_query)
        
        success2 = result2 is not None  # Should handle gracefully
        print_test_result(success2, "Handling invalid chart requests")
        
        return success and success2
        
    except Exception as e:
        print_test_result(False, f"Chart edge case test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Running Chart Query Tests")
    
    test1_result = test_chart_generation()
    test2_result = test_dashboard_creation()
    test3_result = test_chart_customization()
    test4_result = test_chart_edge_cases()
    
    if test1_result and test2_result and test3_result and test4_result:
        print("\n✅ All chart tests passed!")
    else:
        print("\n❌ Some chart tests failed!")
