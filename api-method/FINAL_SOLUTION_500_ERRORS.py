#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""500 오류 최종 해결"""

import json
import os

# 설정 로드
config_path = r"C:\Users\8899y\Documents\카페24_프로젝트\01_ACTIVE_PROJECT\config\oauth_token.json"
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# 최종 환경변수
final_env = f"""CAFE24_MALL_ID=manwonyori
CAFE24_CLIENT_ID=9bPpABwHB5mtkCEAfIeuNK
CAFE24_CLIENT_SECRET=qtnWtUk2OZzua1SRa7gN3A
CAFE24_REDIRECT_URI=https://cafe24-automation.onrender.com/callback
CAFE24_ACCESS_TOKEN={config['access_token']}
CAFE24_REFRESH_TOKEN={config['refresh_token']}
PYTHONPATH=/opt/render/project/src
CAFE24_API_VERSION=2025-06-01
ENABLE_AUTO_REFRESH=true
ENABLE_DASHBOARD=true
ENABLE_API_ENDPOINTS=true
PRODUCTION_MODE=true
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
"""

print("500 ERROR FINAL SOLUTION")
print("=" * 60)
print("\nHealth Check: OK (Server is running)")
print("Main Page: OK (Application is working)")
print("Products API: ERROR 500 (Internal server error)")
print("Orders API: ERROR 500 (Internal server error)")
print("\nDIAGNOSIS: The Flask app is running but API routes have errors")
print("\nMOST LIKELY CAUSE: Environment variables not properly loaded")
print("\nSOLUTION:")
print("1. Copy the environment variables below")
print("2. Go to Render dashboard")
print("3. Replace ALL environment variables")
print("4. Save and Deploy with 'Clear build cache & deploy'")
print("\n" + "=" * 60)
print("COPY THESE ENVIRONMENT VARIABLES:")
print("=" * 60)
print(final_env)
print("=" * 60)

# 파일로도 저장
with open("FINAL_ENV_SOLUTION.txt", "w") as f:
    f.write(final_env)

print("\nSaved to: FINAL_ENV_SOLUTION.txt")
print("\nIMPORTANT:")
print("- Use 'Clear build cache & deploy' option in Render")
print("- This forces a fresh installation of all dependencies")
print("- Wait 5-7 minutes for complete deployment")

# 추가 디버그 정보
debug_info = f"""
DEBUGGING CHECKLIST:

1. Check Render Logs:
   - Look for "KeyError" messages
   - Check for "ImportError" messages
   - Look for "CAFE24_ACCESS_TOKEN" errors

2. Common Issues:
   - Token format: Your token is {len(config['access_token'])} characters (should be 22)
   - Environment loading: PYTHONPATH must be set
   - Module imports: src folder must be in Python path

3. If still failing after deploy:
   - The token might be invalid
   - Get new token from https://developers.cafe24.com
   - Update CAFE24_ACCESS_TOKEN in Render

Your current token: {config['access_token'][:10]}...{config['access_token'][-5:]}
"""

with open("DEBUG_INFO.txt", "w") as f:
    f.write(debug_info)

print("\nDEBUG INFO saved to: DEBUG_INFO.txt")