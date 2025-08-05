#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
최종 배포 확인 및 대안 제시
"""
import requests
import sys
import io
import time

# UTF-8 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_url = 'https://cafe24-automation.onrender.com'

print("=== 최종 배포 확인 ===\n")

# 추가 대기
print("추가로 60초 대기 중...")
for i in range(6):
    print(f"{i*10}/60초...")
    time.sleep(10)

# 재확인
print("\n최종 상태 확인:")
response = requests.get(f'{base_url}/api/debug/token')
if response.status_code == 200:
    token_info = response.json()
    print(f"- 토큰 유효: {token_info.get('is_valid', False)}")
    print(f"- Access Token 미리보기: {token_info.get('env_token_preview', '')}")

print("\n\n=== 대안 해결책 ===")
print("\n1. Render 대시보드에서 수동 배포:")
print("   - https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg")
print("   - 'Manual Deploy' > 'Deploy latest commit' 클릭")

print("\n2. 환경변수 직접 설정:")
print("   - Environment 탭에서 다음 추가:")
print("   - CAFE24_ACCESS_TOKEN = yhep7daQIqcUnu3pBhsyBB")
print("   - CAFE24_REFRESH_TOKEN = Y39VGzKtMxYnXZMr0yLjfF")

print("\n3. 로컬에서 직접 가격 수정:")
print("   - 로컬 서버 실행 (python app.py)")
print("   - http://localhost:5000/margin-dashboard 접속")
print("   - 점보떡볶이 가격 수정")

print("\n4. Render 로그 확인:")
print("   - https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg/logs")
print("   - 배포 오류 메시지 확인")

print("\n\n현재 상황:")
print("- 로컬 토큰은 갱신됨 ✅")
print("- GitHub 푸시 완료 ✅") 
print("- Render 서버 토큰 반영 대기 중 ⏳")
print("\n권장: Render 대시보드에서 수동 배포 또는 환경변수 직접 설정")