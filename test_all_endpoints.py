#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test all Cafe24 API endpoints
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List

class Cafe24Tester:
    def __init__(self, base_url: str = "https://cafe24-automation.onrender.com"):
        self.base_url = base_url
        self.results = []
        self.session = requests.Session()
        
    def test_endpoint(self, name: str, method: str, path: str, 
                     data: Dict = None, expected_status: int = 200) -> bool:
        """Test a single endpoint"""
        url = f"{self.base_url}{path}"
        print(f"\nTesting: {name}")
        print(f"  Method: {method} {path}")
        
        try:
            start_time = time.time()
            
            if method == "GET":
                response = self.session.get(url, timeout=10)
            elif method == "POST":
                response = self.session.post(url, json=data, 
                                           headers={"Content-Type": "application/json"},
                                           timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            elapsed = time.time() - start_time
            
            # Check status code
            success = response.status_code == expected_status
            
            # Parse response
            try:
                response_data = response.json()
            except:
                response_data = response.text
                
            result = {
                "name": name,
                "path": path,
                "method": method,
                "status": response.status_code,
                "success": success,
                "elapsed": f"{elapsed:.2f}s",
                "response": response_data
            }
            
            self.results.append(result)
            
            # Print result
            if success:
                print(f"  [OK] Status: {response.status_code} - Success ({elapsed:.2f}s)")
                # Print sample data
                if isinstance(response_data, dict):
                    if "products" in response_data:
                        print(f"  -> Found {len(response_data['products'])} products")
                    elif "orders" in response_data:
                        print(f"  -> Found {len(response_data['orders'])} orders")
                    elif "customers" in response_data:
                        print(f"  -> Found {len(response_data['customers'])} customers")
                    elif "mode" in response_data:
                        print(f"  -> Mode: {response_data['mode']}")
            else:
                print(f"  [FAIL] Status: {response.status_code} - Failed")
                if isinstance(response_data, dict) and "error" in response_data:
                    print(f"  -> Error: {response_data['error']}")
                    
            return success
            
        except Exception as e:
            print(f"  [ERROR] Exception: {str(e)}")
            self.results.append({
                "name": name,
                "path": path,
                "method": method,
                "success": False,
                "error": str(e)
            })
            return False
            
    def run_all_tests(self):
        """Run all endpoint tests"""
        print("=" * 60)
        print("Cafe24 Automation System - Full Endpoint Test")
        print(f"Target URL: {self.base_url}")
        print(f"Test Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Define all test cases
        tests = [
            # Basic endpoints
            ("Home Page", "GET", "/", None, 200),
            ("Health Check", "GET", "/health", None, 200),
            
            # Product endpoints
            ("Products List", "GET", "/api/products?limit=5", None, 200),
            ("Products with Filter", "GET", "/api/products?selling=T&limit=3", None, 200),
            
            # Order endpoints  
            ("Orders Today", "GET", "/api/orders?limit=5", None, 200),
            ("Orders Date Range", "GET", 
             f"/api/orders?start_date={datetime.now().strftime('%Y-%m-%d')}&limit=3", 
             None, 200),
            
            # Inventory endpoints
            ("Inventory Check", "GET", "/api/inventory?threshold=10", None, 200),
            ("Low Stock Items", "GET", "/api/inventory?threshold=5", None, 200),
            
            # Customer endpoints
            ("Customers List", "GET", "/api/customers?limit=5", None, 200),
            
            # Statistics endpoints
            ("Daily Sales Stats", "GET", "/api/sales/statistics?period=daily", None, 200),
            ("Weekly Sales Stats", "GET", "/api/sales/statistics?period=weekly", None, 200),
            ("Monthly Sales Stats", "GET", "/api/sales/statistics?period=monthly", None, 200),
            
            # Report endpoints
            ("Daily Report", "GET", "/api/report/daily", None, 200),
            ("Inventory Report", "GET", "/api/report/inventory", None, 200),
            ("Sales Report", "GET", "/api/report/sales", None, 200),
            
            # Natural language endpoints
            ("NLP - Products", "POST", "/api/execute", 
             {"command": "show products"}, 200),
            ("NLP - Orders", "POST", "/api/execute", 
             {"command": "check today orders"}, 200),
            ("NLP - Inventory", "POST", "/api/execute", 
             {"command": "low stock items"}, 200),
            
            # Test endpoint
            ("All Tests", "GET", "/api/test/all", None, 200),
        ]
        
        # Run all tests
        for test in tests:
            self.test_endpoint(*test)
            time.sleep(0.5)  # Small delay between tests
            
        # Generate summary
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.get("success", False))
        failed = total - passed
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ({passed/total*100:.1f}%)")
        print(f"Failed: {failed} ({failed/total*100:.1f}%)")
        
        if failed > 0:
            print("\nFailed Tests:")
            for result in self.results:
                if not result.get("success", False):
                    print(f"  - {result['name']}: {result.get('error', 'Status ' + str(result.get('status', 'Unknown')))}")
                    
        # Check mode
        for result in self.results:
            if result.get("name") == "Home Page" and result.get("success"):
                response = result.get("response", {})
                if isinstance(response, dict):
                    mode = response.get("mode", "unknown")
                    print(f"\nSystem Mode: {mode}")
                    if mode == "demo":
                        print("  -> Running in demo mode (API keys required)")
                    break
                    
        print("\nTest Complete!")
        
        # Save results
        filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\nDetailed results saved: {filename}")


def main():
    """Main function"""
    import sys
    
    # Get URL from argument or use default
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "https://cafe24-automation.onrender.com"
        
    # Create tester and run tests
    tester = Cafe24Tester(base_url)
    tester.run_all_tests()


if __name__ == "__main__":
    main()