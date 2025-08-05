#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""새 토큰 적용"""

print("새 토큰을 받았다면 아래에 입력하세요:")
print("(개발자센터에서 발급받은 토큰)")
print()

# 여기에 새 토큰을 붙여넣으세요
NEW_ACCESS_TOKEN = "여기에_새_ACCESS_TOKEN_붙여넣기"
NEW_REFRESH_TOKEN = "여기에_새_REFRESH_TOKEN_붙여넣기"

# 환경변수 파일 생성
env_content = f"""CAFE24_MALL_ID=manwonyori
CAFE24_CLIENT_ID=9bPpABwHB5mtkCEAfIeuNK
CAFE24_CLIENT_SECRET=qtnWtUk2OZzua1SRa7gN3A
CAFE24_REDIRECT_URI=https://cafe24-automation.onrender.com/callback
CAFE24_ACCESS_TOKEN={NEW_ACCESS_TOKEN}
CAFE24_REFRESH_TOKEN={NEW_REFRESH_TOKEN}
PYTHONPATH=/opt/render/project/src
CAFE24_API_VERSION=2025-06-01
ENABLE_AUTO_REFRESH=true
ENABLE_DASHBOARD=true
ENABLE_API_ENDPOINTS=true
PRODUCTION_MODE=true
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
"""

print("파일 편집 방법:")
print("1. 이 파일을 메모장으로 열기")
print("2. NEW_ACCESS_TOKEN = 부분에 새 토큰 붙여넣기")
print("3. NEW_REFRESH_TOKEN = 부분에 새 토큰 붙여넣기")
print("4. 저장 후 다시 실행")
print()
print("그러면 FINAL_NEW_TOKENS.txt 파일이 생성됩니다")

if NEW_ACCESS_TOKEN != "여기에_새_ACCESS_TOKEN_붙여넣기":
    with open("FINAL_NEW_TOKENS.txt", "w") as f:
        f.write(env_content)
    print("\n[SUCCESS] FINAL_NEW_TOKENS.txt 생성됨!")
    print("\n다음 단계:")
    print("1. FINAL_NEW_TOKENS.txt 내용 복사")
    print("2. Render 환경변수에 붙여넣기")
    print("3. Clear build cache & deploy")