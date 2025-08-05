#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test token refresh and API connection
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auto_token_manager import get_token_manager
import requests
import json

def test_token_manager():
    """Test token manager and API connection"""
    print("=" * 60)
    print("Testing Token Manager and API Connection")
    print("=" * 60)
    
    # Get token manager
    manager = get_token_manager()
    
    if not manager.token_data:
        print("❌ No token data found")
        return False
    
    print(f"Mall ID: {manager.token_data.get('mall_id')}")
    print(f"Client ID: {manager.token_data.get('client_id')}")
    print(f"Token expires: {manager.token_data.get('expires_at')}")
    
    # Try to get a valid token
    print("\n[INFO] Getting valid token...")
    token = manager.get_valid_token()
    
    if not token:
        print("[ERROR] Could not get valid token")
        return False
    
    print(f"[OK] Got valid token: {token[:30]}...")
    
    # Test API call
    print("\n[INFO] Testing API call...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'X-Cafe24-Api-Version': '2025-06-01'
    }
    
    test_url = f"https://{manager.token_data['mall_id']}.cafe24api.com/api/v2/admin/products?limit=5"
    
    try:
        response = requests.get(test_url, headers=headers, timeout=10)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])
            print(f"[OK] API call successful! Found {len(products)} products")
            return True
        else:
            print(f"[ERROR] API call failed: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"[ERROR] API call error: {e}")
        return False

if __name__ == "__main__":
    if test_token_manager():
        print("\n[SUCCESS] Token manager is working correctly!")
    else:
        print("\n[FAIL] Token manager test failed")