#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render 서버 종합 진단
"""
import requests
import json
import sys
import io
from datetime import datetime

# UTF-8 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_url = 'https://cafe24-automation.onrender.com'

print("=== Render 서버 종합 진단 ===")
print(f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*50)

# 1. 기본 연결 테스트
print("\n1. 기본 연결 테스트")
print("-"*30)
try:
    response = requests.get(base_url, timeout=10)
    print(f"홈페이지 상태: {response.status_code}")
    print(f"서버 헤더: {response.headers.get('x-render-origin-server', 'N/A')}")
except Exception as e:
    print(f"연결 오류: {e}")

# 2. 현재 설정 상태
print("\n2. 현재 설정 상태")
print("-"*30)
endpoints = [
    ('/api/status', 'API 상태'),
    ('/api/debug/token', '토큰 디버그'),
    ('/health', '헬스체크')
]

for endpoint, desc in endpoints:
    try:
        response = requests.get(f'{base_url}{endpoint}', timeout=10)
        print(f"\n{desc} ({endpoint}):")
        print(f"상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if endpoint == '/api/debug/token':
                print(f"- 토큰 존재: {data.get('has_token', False)}")
                print(f"- 토큰 유효: {data.get('is_valid', False)}")
                print(f"- Mall ID: {data.get('mall_id', 'N/A')}")
                print(f"- 환경변수 토큰: {data.get('env_has_token', False)}")
                print(f"- 파일 토큰: {data.get('file_has_token', False)}")
                if data.get('error'):
                    print(f"- 오류: {data.get('error')}")
            elif endpoint == '/api/status':
                print(f"- 서버 버전: {data.get('server', {}).get('version', 'N/A')}")
                print(f"- Cafe24 API 상태: {data.get('apis', {}).get('cafe24', 'N/A')}")
                print(f"- 인증 상태: {data.get('api_test', {}).get('authenticated', False)}")
    except Exception as e:
        print(f"오류: {e}")

# 3. 제품 API 테스트
print("\n\n3. 제품 API 직접 테스트")
print("-"*30)
product_endpoints = [
    '/api/products/all',
    '/api/margin/analysis',
    '/api/products'
]

for endpoint in product_endpoints:
    print(f"\n{endpoint}:")
    try:
        response = requests.get(f'{base_url}{endpoint}', timeout=10)
        print(f"상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                if 'products' in data:
                    print(f"제품 수: {len(data['products'])}")
                    if len(data['products']) == 0:
                        print("⚠️ 제품 목록이 비어있음")
                if 'error' in data:
                    print(f"오류: {data['error']}")
                if 'success' in data:
                    print(f"성공 여부: {data['success']}")
            elif isinstance(data, list):
                print(f"제품 수: {len(data)}")
        elif response.status_code == 401:
            print("❌ 인증 실패 (401 Unauthorized)")
        elif response.status_code == 404:
            print("❌ 엔드포인트 없음 (404 Not Found)")
        else:
            print(f"오류 응답: {response.text[:100]}...")
    except Exception as e:
        print(f"예외: {e}")

# 4. 문제 진단
print("\n\n4. 문제 진단 결과")
print("-"*30)

# CURL 명령어로 직접 테스트
print("\n5. CURL 명령어 테스트 (명령 프롬프트에서 실행):")
print("-"*30)
print("curl -X GET https://cafe24-automation.onrender.com/api/debug/token")
print("curl -X GET https://cafe24-automation.onrender.com/api/products/all")
print("curl -X GET https://cafe24-automation.onrender.com/api/margin/analysis")

# 6. 브라우저 콘솔 테스트
print("\n\n6. 브라우저 콘솔 테스트 (F12 > Console):")
print("-"*30)
print("""
// 토큰 상태 확인
fetch('/api/debug/token')
  .then(res => res.json())
  .then(data => {
    console.log('토큰 상태:', data);
    console.log('토큰 유효:', data.is_valid);
    console.log('토큰 존재:', data.has_token);
  });

// 제품 목록 확인
fetch('/api/margin/analysis')
  .then(res => {
    console.log('상태 코드:', res.status);
    return res.json();
  })
  .then(data => {
    console.log('응답:', data);
    if (data.products) {
      console.log('제품 수:', data.products.length);
    }
  })
  .catch(err => console.error('오류:', err));
""")

# 7. 권장 조치
print("\n\n7. 권장 조치:")
print("-"*30)
print("1. Render 로그 확인:")
print("   https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg/logs")
print("\n2. 환경변수 재확인:")
print("   - CAFE24_ACCESS_TOKEN이 설정되어 있는지")
print("   - CAFE24_MALL_ID가 'manwonyori'로 설정되어 있는지")
print("\n3. 서비스 재시작:")
print("   - Render 대시보드에서 'Restart Service' 클릭")
print("\n4. 로컬 테스트:")
print("   - 로컬에서는 정상 작동하는지 확인")