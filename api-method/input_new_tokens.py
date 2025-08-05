#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
새 토큰 즉시 적용
"""

import json
import os
from datetime import datetime, timedelta

print("=" * 80)
print("NEW TOKEN APPLICATION")
print("=" * 80)

print("\n새로 받은 토큰을 입력해주세요:")
print("(Cafe24 개발자센터에서 방금 발급받은 토큰)")

# 직접 입력 받기
access_token = input("\nAccess Token: ").strip()
refresh_token = input("Refresh Token: ").strip()

if not access_token:
    print("\n[ERROR] Access Token is required!")
    exit(1)

# 1. 로컬 설정 업데이트
config_path = r"C:\Users\8899y\Documents\카페24_프로젝트\01_ACTIVE_PROJECT\config\oauth_token.json"

if os.path.exists(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    config['access_token'] = access_token
    config['refresh_token'] = refresh_token or config.get('refresh_token', '')
    config['expires_at'] = (datetime.now() + timedelta(hours=2)).isoformat()
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("\n[OK] Local config updated")

# 2. Render 환경변수 생성
env_content = f"""# NEW TOKENS - APPLY IMMEDIATELY
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

CAFE24_MALL_ID=manwonyori
CAFE24_CLIENT_ID=9bPpABwHB5mtkCEAfIeuNK
CAFE24_CLIENT_SECRET=qtnWtUk2OZzua1SRa7gN3A
CAFE24_REDIRECT_URI=https://cafe24-automation.onrender.com/callback
CAFE24_ACCESS_TOKEN={access_token}
CAFE24_REFRESH_TOKEN={refresh_token or config.get('refresh_token', '')}
PYTHONPATH=/opt/render/project/src
CAFE24_API_VERSION=2025-06-01
ENABLE_AUTO_REFRESH=true
ENABLE_DASHBOARD=true
ENABLE_API_ENDPOINTS=true
PRODUCTION_MODE=true
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
"""

filename = "NEW_TOKENS_APPLY_NOW.txt"
with open(filename, "w") as f:
    f.write(env_content)

print(f"\n[OK] {filename} created")

# 3. 토큰 테스트
print("\n[TESTING] New token...")

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
        print(f"Found {len(data.get('products', []))} products")
    else:
        print(f"[ERROR] Token test failed: {response.status_code}")
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"[ERROR] Test failed: {e}")

print("\n" + "=" * 80)
print("NEXT STEPS:")
print("=" * 80)
print(f"1. Copy contents of {filename}")
print("2. Go to Render Environment tab")
print("3. DELETE all existing variables")
print("4. Paste new variables")
print("5. Save Changes")
print("6. Manual Deploy → Clear build cache & deploy")
print("\nYour system will work after deployment!")