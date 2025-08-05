#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 제품 검색
"""
import requests
import json

# 로컬 서버로 요청
base_url = 'http://localhost:5000'

print("=== 제품 목록 확인 ===\n")

# 1. 전체 제품 목록
try:
    response = requests.get(f'{base_url}/api/products')
    print(f"상태 코드: {response.status_code}")
    
    if response.status_code == 200:
        products = response.json()
        print(f"총 제품 수: {len(products)}")
        
        # 점보떡볶이 검색
        found = False
        for product in products:
            product_name = str(product.get('product_name', ''))
            if '점보' in product_name or '떡볶' in product_name:
                print(f"\n✅ 찾은 제품:")
                print(f"- 상품코드: {product.get('product_no')}")
                print(f"- 상품명: {product_name}")
                print(f"- 판매가: {product.get('price', 0):,}원")
                print(f"- 공급가: {product.get('supply_price', 0):,}원")
                found = True
        
        if not found:
            print("\n모든 제품 목록 (처음 10개):")
            for i, product in enumerate(products[:10]):
                print(f"{i+1}. {product.get('product_name')} (코드: {product.get('product_no')})")
    else:
        print(f"오류: {response.text}")
        
except Exception as e:
    print(f"오류 발생: {e}")

# 2. 자연어 검색 시도
print("\n\n=== 자연어 검색 ===")
try:
    command_data = {
        "command": "점보떡볶이 찾아줘"
    }
    
    response = requests.post(f'{base_url}/api/execute', json=command_data)
    print(f"상태 코드: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(json.dumps(result, indent=2, ensure_ascii=False)[:500])
        
except Exception as e:
    print(f"오류 발생: {e}")