#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render 대시보드 직접 접근 테스트
"""
import requests
import json
import sys
import io
from bs4 import BeautifulSoup

# UTF-8 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Render 서버 URL
base_url = 'https://cafe24-automation.onrender.com'

print("=== Render 대시보드 접근 테스트 ===\n")

# 1. 메인 대시보드 확인
print("1. 메인 대시보드:")
response = requests.get(f'{base_url}/dashboard')
print(f"상태 코드: {response.status_code}")

# 2. 마진 대시보드 확인
print("\n2. 마진 대시보드:")
response = requests.get(f'{base_url}/margin-dashboard')
print(f"상태 코드: {response.status_code}")

if response.status_code == 200:
    print("✅ 마진 대시보드 접속 성공")
    
    # HTML 파싱해서 API 엔드포인트 찾기
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 스크립트 태그에서 API 호출 패턴 찾기
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string and 'fetch' in script.string:
            # API 엔드포인트 패턴 추출
            if '/api/' in script.string:
                print("\n발견된 API 패턴:")
                lines = script.string.split('\n')
                for line in lines:
                    if '/api/' in line and 'fetch' in line:
                        print(f"- {line.strip()[:100]}...")

# 3. 가능한 API 엔드포인트 테스트
print("\n\n3. API 엔드포인트 테스트:")
endpoints = [
    '/api/status',
    '/api/products/all',
    '/api/margin/products',
    '/api/products?limit=10',
    '/margin/api/products'
]

for endpoint in endpoints:
    print(f"\n테스트: {endpoint}")
    try:
        response = requests.get(f'{base_url}{endpoint}')
        print(f"상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"✅ 성공! {len(data)}개 항목")
                # 점보떡볶이 찾기
                for item in data:
                    if '점보' in str(item.get('product_name', '')):
                        print(f"\n🎯 점보떡볶이 발견!")
                        print(f"제품: {item}")
                        break
            else:
                print(f"응답 타입: {type(data)}")
    except Exception as e:
        print(f"오류: {str(e)}")

print("\n\n=== 결론 ===")
print("브라우저에서 직접 마진 대시보드를 사용하는 것이 가장 확실합니다:")
print("1. https://cafe24-automation.onrender.com/margin-dashboard 접속")
print("2. 페이지 로드 완료 대기")
print("3. 제품 목록에서 '점보떡볶이' 검색")
print("4. 가격 수정 진행")