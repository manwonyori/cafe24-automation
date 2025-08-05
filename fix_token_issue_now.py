#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
토큰 문제 즉시 해결
"""
import sys
import io

# UTF-8 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=== 토큰 문제 해결 가이드 ===\n")

print("문제: 환경변수에 토큰이 있지만 유효하지 않음\n")

print("해결 방법 1: Render 환경변수 업데이트")
print("-"*40)
print("1. https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg/env 접속")
print("2. 다음 변수 확인/업데이트:")
print("   CAFE24_ACCESS_TOKEN = yhep7daQIqcUnu3pBhsyBB")
print("   CAFE24_REFRESH_TOKEN = Y39VGzKtMxYnXZMr0yLjfF")
print("3. Save Changes 클릭")
print("4. 서비스 재시작 대기 (2-3분)")

print("\n해결 방법 2: 서비스 수동 재시작")
print("-"*40)
print("1. Render 대시보드에서 'Restart Service' 클릭")
print("2. 또는 'Manual Deploy' > 'Clear build cache & deploy' 선택")

print("\n해결 방법 3: 데모 모드 확인")
print("-"*40)
print("app.py에서 DEMO_MODE가 True로 설정되어 있을 수 있음")
print("GitHub에서 app.py 확인 필요")

print("\n브라우저에서 확인할 사항:")
print("-"*40)
print("1. F12 (개발자 도구) 열기")
print("2. Console 탭에서 다음 실행:")
print("""
fetch('/api/debug/token')
  .then(r => r.json())
  .then(d => console.log('토큰 디버그:', d));
""")

print("\n가장 빠른 해결책:")
print("-"*40)
print("로컬에서 작업 진행:")
print("1. 로컬 서버가 이미 실행 중")
print("2. http://localhost:5000/margin-dashboard 접속")
print("3. 여기서는 토큰이 정상 작동함")
print("4. 점보떡볶이 가격 수정 가능")