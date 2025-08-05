#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
마진 대시보드 API 직접 테스트
"""
import requests
import json
import sys
import io

# UTF-8 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_url = 'https://cafe24-automation.onrender.com'

print("=== 마진 대시보드 API 문제 진단 ===\n")

# 1. 기본 서버 상태
print("1. 서버 상태 확인:")
response = requests.get(f'{base_url}/api/status')
print(f"상태 코드: {response.status_code}")
if response.status_code == 200:
    print("✅ 서버 정상 작동")

# 2. 토큰 상태 재확인
print("\n2. 토큰 상태:")
response = requests.get(f'{base_url}/api/debug/token')
if response.status_code == 200:
    token_info = response.json()
    print(f"토큰 유효: {token_info.get('is_valid', False)}")
    print(f"토큰 존재: {token_info.get('has_token', False)}")
    if token_info.get('error'):
        print(f"오류: {token_info.get('error')}")

# 3. 마진 분석 API 직접 호출
print("\n3. 마진 분석 API 테스트:")
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

response = requests.get(f'{base_url}/api/margin/analysis', headers=headers)
print(f"상태 코드: {response.status_code}")
print(f"응답 헤더: {dict(response.headers)}")

if response.status_code == 200:
    try:
        data = response.json()
        print(f"응답 타입: {type(data)}")
        print(f"키: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
        
        if 'products' in data:
            products = data['products']
            print(f"제품 수: {len(products)}")
            
            if products:
                print("\n제품 샘플:")
                for i, product in enumerate(products[:3]):
                    print(f"{i+1}. {product.get('product_name', 'N/A')}")
        
        if 'error' in data:
            print(f"오류 메시지: {data['error']}")
            
    except Exception as e:
        print(f"JSON 파싱 오류: {e}")
        print(f"응답 내용: {response.text[:200]}...")
else:
    print(f"오류 응답: {response.text[:200]}...")

# 4. 다른 제품 API 테스트
print("\n\n4. 대체 API 엔드포인트 테스트:")
alternative_endpoints = [
    '/api/products/all',
    '/api/products',
    '/api/margin/products',
    '/margin-dashboard/api/products'
]

for endpoint in alternative_endpoints:
    print(f"\n테스트: {endpoint}")
    try:
        response = requests.get(f'{base_url}{endpoint}', headers=headers, timeout=10)
        print(f"상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'products' in data:
                print(f"✅ 성공! 제품 수: {len(data['products'])}")
                break
            elif isinstance(data, list):
                print(f"✅ 성공! 제품 수: {len(data)}")
                break
    except Exception as e:
        print(f"오류: {str(e)}")

# 5. 브라우저 콘솔에서 실행할 JavaScript
print("\n\n5. 브라우저 콘솔에서 직접 테스트:")
print("마진 대시보드 페이지에서 F12 > Console 탭에서 실행:")
print("""
fetch('/api/margin/analysis')
  .then(res => res.json())
  .then(data => console.log(data))
  .catch(err => console.error(err));
""")

print("\n\n6. 가능한 해결책:")
print("1. 브라우저 캐시 지우기 (Ctrl+F5)")
print("2. 시크릿 모드에서 접속")
print("3. 개발자 도구 Network 탭에서 실패한 요청 확인")
print("4. 로컬에서 테스트: http://localhost:5000/margin-dashboard")