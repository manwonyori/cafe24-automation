#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API를 통해 제품 검색
"""
import requests
import json
import sys
import io

# UTF-8 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# API 서버 URL
base_url = 'https://cafe24-automation.onrender.com'

# 1. 먼저 전체 제품 목록 확인
print("=== 제품 목록 API 테스트 ===\n")

# 자연어 명령으로 검색
print("1. 자연어 명령으로 제품 검색:")
command_data = {
    "command": "점보떡볶이 제품 보여줘"
}

response = requests.post(f'{base_url}/api/execute', json=command_data)
print(f"상태 코드: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    print(f"응답: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}...")
    
    # 제품 정보 추출
    if 'data' in result:
        products = result['data']
        for product in products:
            if '점보떡볶' in product.get('product_name', ''):
                print(f"\n✅ 찾은 제품:")
                print(f"- 상품명: {product.get('product_name')}")
                print(f"- 판매가: {product.get('price', 0):,}원")
                print(f"- 공급가: {product.get('supply_price', 0):,}원")

# 2. 전체 제품 목록 API 시도
print("\n\n2. 전체 제품 목록 API:")
response = requests.get(f'{base_url}/api/products')
print(f"상태 코드: {response.status_code}")

if response.status_code == 200:
    products = response.json()
    print(f"총 제품 수: {len(products)}")
    
    # 점보떡볶이 검색
    for product in products:
        if '점보' in str(product.get('product_name', '')):
            print(f"\n찾은 제품: {product}")
            break