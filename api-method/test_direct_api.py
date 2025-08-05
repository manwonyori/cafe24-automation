#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cafe24 API 직접 테스트
"""
import requests
import json

# 토큰 읽기
with open('oauth_token.json', 'r', encoding='utf-8') as f:
    token_data = json.load(f)

access_token = token_data['access_token']
mall_id = token_data['mall_id']

# 다양한 API 버전 테스트
api_versions = ['2024-06-01', '2024-09-01', '2024-12-01', '2025-01-01']

for version in api_versions:
    print(f"\n=== Testing API Version: {version} ===")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Cafe24-Api-Version': version
    }
    
    url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products/count"
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Success! Response: {response.text}")
            print(f"✓ API Version {version} works!")
            break
        else:
            print(f"Error: {response.text[:200]}")
    except Exception as e:
        print(f"Exception: {str(e)}")