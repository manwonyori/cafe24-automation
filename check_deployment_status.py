#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render 배포 상태 확인
"""
import requests
import time
import sys
import io

# UTF-8 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_url = 'https://cafe24-automation.onrender.com'

print("=== Render 재배포 상태 확인 ===\n")
print("GitHub 푸시 완료. Render가 자동 배포 중입니다...")
print("일반적으로 2-3분 소요됩니다.\n")

# 30초 대기
for i in range(6):
    print(f"대기 중... {i*10}/60초")
    time.sleep(10)

print("\n배포 상태 확인 중...\n")

# 1. 서버 상태 확인
response = requests.get(f'{base_url}/api/status')
print(f"서버 상태: {response.status_code}")

# 2. 토큰 상태 확인
response = requests.get(f'{base_url}/api/debug/token')
if response.status_code == 200:
    token_info = response.json()
    print(f"\n토큰 상태:")
    print(f"- 토큰 존재: {token_info.get('has_token', False)}")
    print(f"- 토큰 유효: {token_info.get('is_valid', False)}")
    print(f"- Access Token: ***{token_info.get('env_token_preview', '')[-10:]}")

# 3. 제품 API 테스트
print("\n제품 API 테스트:")
response = requests.get(f'{base_url}/api/products/all')
print(f"상태 코드: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    if 'products' in data:
        products = data['products']
        print(f"✅ 제품 목록 로드 성공! {len(products)}개 제품")
        
        # 점보떡볶이 찾기
        for product in products:
            if '점보떡볶' in str(product.get('product_name', '')):
                print(f"\n🎯 [인생]점보떡볶이1490g 발견!")
                print(f"- 상품명: {product.get('product_name')}")
                print(f"- 현재 가격: {product.get('price', 0):,}원")
                print(f"- 공급가: {product.get('supply_price', 0):,}원")
                break
    else:
        print("❌ 아직 제품 데이터가 로드되지 않았습니다.")
else:
    print("❌ API 호출 실패. 배포가 진행 중일 수 있습니다.")

print("\n\n다음 단계:")
print("1. 배포 완료 대기 (1-2분 추가)")
print("2. https://cafe24-automation.onrender.com/margin-dashboard 접속")
print("3. 점보떡볶이 제품 검색 및 가격 수정")