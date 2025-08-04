#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wait for Render deployment and test endpoints
"""

import time
import requests
import json
from datetime import datetime


def check_deployment_status(base_url):
    """Check if new endpoints are deployed"""
    test_endpoints = [
        "/api/customers?limit=1",
        "/api/sales/statistics?period=daily",
        "/api/test/all"
    ]
    
    print(f"\nChecking deployment status at {base_url}...")
    
    for endpoint in test_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"  [OK] {endpoint} - New deployment detected!")
                return True
            else:
                print(f"  [WAITING] {endpoint} - Status {response.status_code}")
        except Exception as e:
            print(f"  [ERROR] {endpoint} - {str(e)}")
            
    return False


def main():
    base_url = "https://cafe24-automation.onrender.com"
    max_wait = 300  # 5 minutes
    check_interval = 30  # Check every 30 seconds
    
    print("=" * 60)
    print("Cafe24 Deployment Monitor")
    print(f"Monitoring: {base_url}")
    print(f"Max wait time: {max_wait} seconds")
    print("=" * 60)
    
    start_time = time.time()
    deployed = False
    
    while time.time() - start_time < max_wait:
        if check_deployment_status(base_url):
            deployed = True
            break
            
        elapsed = int(time.time() - start_time)
        remaining = max_wait - elapsed
        print(f"\nWaiting for deployment... ({elapsed}s elapsed, {remaining}s remaining)")
        print("Render typically takes 2-5 minutes to deploy...")
        
        time.sleep(check_interval)
        
    if deployed:
        print("\n" + "=" * 60)
        print("SUCCESS! New deployment is live!")
        print("Running full test suite...")
        print("=" * 60)
        
        # Run the full test
        import test_all_endpoints
        tester = test_all_endpoints.Cafe24Tester(base_url)
        tester.run_all_tests()
    else:
        print("\n" + "=" * 60)
        print("TIMEOUT! Deployment not detected within time limit.")
        print("Please check Render dashboard manually.")
        print("=" * 60)


if __name__ == "__main__":
    main()