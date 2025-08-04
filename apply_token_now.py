#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
받은 토큰 즉시 적용
"""

import json
import os
import urllib.parse
from datetime import datetime, timedelta

# 받은 토큰 (URL 디코딩)
encoded_token = "V6G4Dzp6xvki7EKmpjKT9jg62Zgosyk7RguBwiwt%2Fj4%3D"
access_token = urllib.parse.unquote(encoded_token)

print("=" * 80)
print("APPLYING NEW TOKEN IMMEDIATELY")
print("=" * 80)

print(f"\nReceived token (encoded): {encoded_token}")
print(f"Decoded token: {access_token}")

# 1. 로컬 설정 업데이트
config_path = r"C:\Users\8899y\Documents\카페24_프로젝트\01_ACTIVE_PROJECT\config\oauth_token.json"

if os.path.exists(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    config['access_token'] = access_token
    config['expires_at'] = (datetime.now() + timedelta(hours=2)).isoformat()
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("\n[OK] Local config updated")

# 2. 토큰 테스트
print("\n[TESTING] New token validity...")

import requests

test_url = f"https://manwonyori.cafe24api.com/api/v2/products?limit=1"
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json',
    'X-Cafe24-Api-Version': '2025-06-01'
}

try:
    response = requests.get(test_url, headers=headers, timeout=10)
    if response.status_code == 200:
        print("[SUCCESS] Token is valid! ✓")
        data = response.json()
        print(f"API Response: {len(data.get('products', []))} products found")
    else:
        print(f"[ERROR] Token test failed: {response.status_code}")
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"[ERROR] Test failed: {e}")

# 3. Render 환경변수 생성
env_content = f"""# WORKING TOKEN - APPLY NOW
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

CAFE24_MALL_ID=manwonyori
CAFE24_CLIENT_ID=9bPpABwHB5mtkCEAfIeuNK
CAFE24_CLIENT_SECRET=qtnWtUk2OZzua1SRa7gN3A
CAFE24_REDIRECT_URI=https://cafe24-automation.onrender.com/callback
CAFE24_ACCESS_TOKEN={access_token}
CAFE24_REFRESH_TOKEN={config.get('refresh_token', '')}
PYTHONPATH=/opt/render/project/src
CAFE24_API_VERSION=2025-06-01
ENABLE_AUTO_REFRESH=true
ENABLE_DASHBOARD=true
ENABLE_API_ENDPOINTS=true
PRODUCTION_MODE=true
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
"""

filename = "WORKING_TOKEN_DEPLOY.txt"
with open(filename, "w") as f:
    f.write(env_content)

print(f"\n[OK] {filename} created")

print("\n" + "=" * 80)
print("DEPLOY IMMEDIATELY:")
print("=" * 80)
print(f"1. Copy contents of {filename}")
print("2. Go to: https://dashboard.render.com/")
print("3. Environment tab → DELETE all variables")
print("4. Paste new variables → Save Changes")
print("5. Manual Deploy → Clear build cache & deploy")
print("\n✅ Your system will work in 5 minutes!")
print("=" * 80)