#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 API 테스트
"""
import requests
import json

print("=== 로컬 API 테스트 ===\n")

# 1. API 상태 확인
response = requests.get('http://localhost:5000/api/status')
print(f"API 상태: {response.status_code}")
if response.status_code == 200:
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# 2. 제품 목록 (limit 10)
print("\n\n=== 제품 목록 (10개) ===")
response = requests.get('http://localhost:5000/api/products?limit=10')
print(f"상태 코드: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"응답 타입: {type(data)}")
    
    if isinstance(data, dict) and 'products' in data:
        products = data['products']
        print(f"제품 수: {len(products)}")
        
        # 점보떡볶이 찾기
        for product in products:
            product_name = product.get('product_name', '')
            if '점보' in product_name or '떡볶' in product_name:
                print(f"\n✅ 찾음: {product_name}")
                print(f"- 상품코드: {product.get('product_no')}")
                print(f"- 가격: {product.get('price')}")
    elif isinstance(data, list):
        print(f"리스트로 반환됨, 길이: {len(data)}")
        # 처음 3개만 출력
        for i, item in enumerate(data[:3]):
            print(f"\n제품 {i+1}: {item}")
else:
    print(f"오류: {response.text[:200]}")