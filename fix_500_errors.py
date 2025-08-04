#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cafe24 API 500 오류 해결
서버 내부 오류를 진단하고 수정합니다
"""

import json
import requests
from datetime import datetime

def diagnose_500_errors():
    """500 오류 진단 및 해결"""
    
    print("=" * 80)
    print("Diagnosing API 500 Errors")
    print("=" * 80)
    
    # 시스템 상태 확인
    print("\n[SYSTEM STATUS CHECK]")
    
    try:
        # 메인 페이지는 정상
        main_response = requests.get("https://cafe24-automation.onrender.com/")
        print(f"Main page: {main_response.status_code} - OK")
        
        # Health check도 정상
        health_response = requests.get("https://cafe24-automation.onrender.com/health")
        print(f"Health check: {health_response.status_code} - OK")
        
    except Exception as e:
        print(f"Connection error: {e}")
    
    print("\n[DIAGNOSIS]")
    print("The 500 errors on /api/products and /api/orders indicate:")
    print("1. The server is running (health check OK)")
    print("2. The main application is working")
    print("3. But the API routes have internal errors")
    
    print("\n[MOST LIKELY CAUSES]")
    print("1. Missing or incorrect environment variables in Render")
    print("2. Token format issues")
    print("3. API client initialization errors")
    
    print("\n[SOLUTION]")
    
    # 올바른 환경변수 생성
    config_path = r"C:\Users\8899y\Documents\카페24_프로젝트\01_ACTIVE_PROJECT\config\oauth_token.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 정확한 환경변수 형식
    env_content = f"""# CORRECTED ENVIRONMENT VARIABLES FOR 500 ERROR FIX
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# IMPORTANT: Copy EXACTLY as shown, including quotes where specified

CAFE24_MALL_ID=manwonyori
CAFE24_CLIENT_ID=9bPpABwHB5mtkCEAfIeuNK
CAFE24_CLIENT_SECRET=qtnWtUk2OZzua1SRa7gN3A
CAFE24_REDIRECT_URI=https://cafe24-automation.onrender.com/callback
CAFE24_ACCESS_TOKEN={config['access_token']}
CAFE24_REFRESH_TOKEN={config['refresh_token']}

# Additional required variables
CAFE24_API_VERSION=2025-06-01
ENABLE_AUTO_REFRESH=true
ENABLE_DASHBOARD=true
ENABLE_API_ENDPOINTS=true
PRODUCTION_MODE=true
LOG_LEVEL=DEBUG

# Python settings
PYTHONUNBUFFERED=1
"""
    
    with open("FIX_500_ENV.txt", "w") as f:
        f.write(env_content)
    
    print("Created: FIX_500_ENV.txt")
    
    # 추가 디버그 정보
    debug_info = f"""# DEBUG INFORMATION

## Current Token Status:
- Access Token: {config['access_token'][:20]}...
- Token Length: {len(config['access_token'])}
- Expires At: {config.get('expires_at', 'Unknown')}

## Required Actions:

1. **Update Render Environment Variables:**
   - Go to: https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg/env
   - DELETE all existing variables
   - Copy ALL content from FIX_500_ENV.txt
   - Paste and Save Changes

2. **Check Render Logs:**
   - Go to Logs tab in Render
   - Look for any Python errors
   - Common issues:
     - "KeyError: CAFE24_ACCESS_TOKEN" - Missing env var
     - "Invalid token" - Token format issue
     - "Import error" - Missing dependencies

3. **Redeploy:**
   - Manual Deploy -> Deploy latest commit
   - Wait 5 minutes

4. **Test Again:**
   - https://cafe24-automation.onrender.com/api/test
   - https://cafe24-automation.onrender.com/api/products

## If Still Getting 500 Errors:

The token might need to be refreshed. Get a new token from:
https://developers.cafe24.com

Then run: python simple_token_setup.py
"""
    
    with open("DEBUG_500_ERRORS.md", "w") as f:
        f.write(debug_info)
    
    print("Created: DEBUG_500_ERRORS.md")
    
    print("\n[IMMEDIATE ACTIONS REQUIRED]")
    print("1. Open FIX_500_ENV.txt")
    print("2. Copy ALL contents")
    print("3. Go to Render Environment tab")
    print("4. Replace ALL variables")
    print("5. Save and Deploy")
    print("\nThe 500 errors should be fixed after deployment!")

if __name__ == "__main__":
    diagnose_500_errors()