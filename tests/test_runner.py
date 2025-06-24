"""
Comprehensive Test Runner
========================
Runs all three use case tests and provides summary
"""

from test_config import check_servers_running, print_test_header, print_test_result
from test_sql_queries import test_sql_basic_queries, test_sql_edge_cases
from test_insight_queries import test_insight_generation, test_trend_analysis, test_anomaly_detection
from test_chart_queries import test_chart_generation, test_dashboard_creation, test_chart_customization, test_chart_edge_cases

def run_all_tests():
    """Run comprehensive test suite for all three use cases"""
    print("🚀 Enterprise Insights Copilot - Comprehensive Test Suite")
    print("=" * 80)
    
    # Check server status
    server_status = check_servers_running()
    if not server_status["backend"]:
        print_test_result(False, "Backend server not running - cannot proceed with tests")
        print("\n💡 Please start the backend server with: conda activate munna && cd backend && python main.py")
        return False
    
    print_test_result(True, f"Backend server running at {server_status['backend_url']}")
    
    # Test results tracking
    results = {}
    
    # SQL Query Tests
    print_test_header("USE CASE 1: SQL QUERY TESTS")
    results['sql_basic'] = test_sql_basic_queries()
    results['sql_edge'] = test_sql_edge_cases()
    
    # Insight Query Tests  
    print_test_header("USE CASE 2: INSIGHT QUERY TESTS")
    results['insight_generation'] = test_insight_generation()
    results['trend_analysis'] = test_trend_analysis()
    results['anomaly_detection'] = test_anomaly_detection()
    
    # Chart Query Tests
    print_test_header("USE CASE 3: CHART QUERY TESTS")
    results['chart_generation'] = test_chart_generation()
    results['dashboard_creation'] = test_dashboard_creation()
    results['chart_customization'] = test_chart_customization()
    results['chart_edge_cases'] = test_chart_edge_cases()
    
    # Summary
    print_test_header("TEST SUMMARY")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    print("\nDetailed Results:")
    
    test_categories = {
        "SQL Queries": ['sql_basic', 'sql_edge'],
        "Insight Generation": ['insight_generation', 'trend_analysis', 'anomaly_detection'],
        "Chart Generation": ['chart_generation', 'dashboard_creation', 'chart_customization', 'chart_edge_cases']
    }
      for category, test_names in test_categories.items():
        category_passed = sum(1 for test_name in test_names if results.get(test_name, False))
        category_total = len(test_names)
        status = "✅" if category_passed == category_total else "⚠️"
        print(f"  {status} {category}: {category_passed}/{category_total}")
        
        for test_name in test_names:
            test_status = "✅ PASS" if results.get(test_name, False) else "❌ FAIL"
            print(f"    • {test_name.replace('_', ' ').title()}: {test_status}")
    
    overall_success = passed == total
    
    if overall_success:
        print("\n🎉 ALL TESTS PASSED! Your Enterprise Insights Copilot is fully functional.")
        print("✅ SQL queries work correctly")
        print("✅ Insight generation is operational") 
        print("✅ Chart generation is working")
        print(f"\n🌐 Frontend available at: {server_status['frontend_url']}")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the detailed results above.")
        print("💡 Consider reviewing the failed components.")
    
    return overall_success

if __name__ == "__main__":
    run_all_tests()
