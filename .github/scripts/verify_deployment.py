#!/usr/bin/env python3
"""
Verify deployment status and mode
"""

import requests
import time
import sys
import json


def verify_deployment(max_retries=10, retry_delay=30):
    """Verify the deployment is live and in production mode"""
    url = "https://cafe24-automation.onrender.com"
    
    print("🔍 Verifying deployment...")
    print(f"URL: {url}")
    print("=" * 50)
    
    for attempt in range(max_retries):
        try:
            print(f"\n📡 Attempt {attempt + 1}/{max_retries}")
            
            # Check main endpoint
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                mode = data.get('mode', 'unknown')
                status = data.get('status', 'unknown')
                
                print(f"   Status Code: {response.status_code}")
                print(f"   System Status: {status}")
                print(f"   System Mode: {mode}")
                
                if mode == 'production':
                    print("\n✅ Production mode active!")
                    
                    # Additional API tests
                    test_endpoints = [
                        '/api/products?limit=1',
                        '/api/orders?limit=1',
                        '/health'
                    ]
                    
                    print("\n🧪 Testing API endpoints:")
                    all_passed = True
                    
                    for endpoint in test_endpoints:
                        test_url = f"{url}{endpoint}"
                        try:
                            test_response = requests.get(test_url, timeout=5)
                            if test_response.status_code == 200:
                                print(f"   ✅ {endpoint}")
                            else:
                                print(f"   ❌ {endpoint} - Status: {test_response.status_code}")
                                all_passed = False
                        except Exception as e:
                            print(f"   ❌ {endpoint} - Error: {str(e)}")
                            all_passed = False
                            
                    if all_passed:
                        print("\n🎉 All tests passed!")
                        return True
                    else:
                        print("\n⚠️  Some tests failed")
                        
                elif mode == 'demo':
                    print("\n⚠️  Still in demo mode. Environment variables may not be synced yet.")
                    print("   Waiting for next attempt...")
                    
            elif response.status_code == 503:
                print("   ⏳ Service unavailable (deployment in progress)")
                
            else:
                print(f"   ❌ Unexpected status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Connection error: {str(e)}")
            
        if attempt < max_retries - 1:
            print(f"   ⏰ Waiting {retry_delay} seconds before retry...")
            time.sleep(retry_delay)
            
    print("\n❌ Deployment verification failed after all attempts")
    return False


if __name__ == "__main__":
    success = verify_deployment()
    sys.exit(0 if success else 1)