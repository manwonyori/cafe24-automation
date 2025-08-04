#!/usr/bin/env python3
"""
Generate deployment test report
"""

import json
import os
import glob
from datetime import datetime


def generate_report():
    """Generate a summary report of test results"""
    print("📊 Generating deployment report...")
    
    # Find test result files
    result_files = glob.glob("test_results_*.json")
    
    if not result_files:
        print("No test results found")
        return
        
    # Use the latest result file
    latest_file = max(result_files)
    
    with open(latest_file, 'r') as f:
        results = json.load(f)
        
    # Generate summary
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r.get('success', False))
    failed_tests = total_tests - passed_tests
    
    report = {
        "deployment_time": datetime.now().isoformat(),
        "test_summary": {
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
        },
        "failed_tests": []
    }
    
    # Collect failed tests
    for result in results:
        if not result.get('success', False):
            report['failed_tests'].append({
                "name": result.get('name'),
                "endpoint": result.get('path'),
                "error": result.get('error', f"Status {result.get('status', 'Unknown')}")
            })
            
    # Determine deployment status
    if failed_tests == 0:
        report['deployment_status'] = "SUCCESS"
        report['message'] = "All tests passed. Deployment successful!"
    else:
        report['deployment_status'] = "PARTIAL"
        report['message'] = f"{failed_tests} tests failed. Check failed tests for details."
        
    # Write report
    report_file = f"deployment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
        
    # Print summary
    print("\n" + "=" * 50)
    print("DEPLOYMENT REPORT")
    print("=" * 50)
    print(f"Time: {report['deployment_time']}")
    print(f"Status: {report['deployment_status']}")
    print(f"Tests: {passed_tests}/{total_tests} passed ({report['test_summary']['success_rate']})")
    
    if report['failed_tests']:
        print("\nFailed Tests:")
        for test in report['failed_tests']:
            print(f"  - {test['name']}: {test['error']}")
            
    print("\n" + report['message'])
    print("=" * 50)
    
    return report['deployment_status'] == "SUCCESS"


if __name__ == "__main__":
    generate_report()