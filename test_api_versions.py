#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
"""
다른 API 버전과 방법 시도
"""
import requests
import json
import time

print("=== Cafe24 API 다양한 방법 테스트 ===\n")

with open('oauth_token.json', 'r', encoding='utf-8') as f:
    token_data = json.load(f)

mall_id = token_data['mall_id']
access_token = token_data['access_token']
PRODUCT_NO = 209

# 다양한 API 버전 시도
api_versions = [
    '2025-06-01',
    '2024-06-01', 
    '2024-03-01',
    '2023-06-01'
]

print("1. 다양한 API 버전으로 시도...")
for version in api_versions:
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Cafe24-Api-Version': version
    }
    
    update_data = {
        "request": {
            "product": {
                "price": "13500"
            }
        }
    }
    
    url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products/{PRODUCT_NO}"
    response = requests.put(url, headers=headers, json=update_data)
    print(f"- 버전 {version}: {response.status_code}")
    
    if response.status_code == 200:
        # 바로 확인
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            price = response.json().get('product', {}).get('price')
            print(f"  현재 가격: {price}")
            if price == "13500.00":
                print("  ✅ 성공!")
                break
    
    time.sleep(1)  # API 제한 방지

# 2. 다른 방법: PATCH 메소드 시도
print("\n2. PATCH 메소드 시도...")
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json',
    'X-Cafe24-Api-Version': '2025-06-01'
}

try:
    response = requests.patch(url, headers=headers, json=update_data)
    print(f"PATCH 응답: {response.status_code}")
except Exception as e:
    print(f"PATCH 오류: {e}")

# 3. 상품 상태 확인
print("\n3. 상품 판매 상태 확인...")
response = requests.get(url, headers=headers)
if response.status_code == 200:
    product = response.json().get('product', {})
    print(f"- selling: {product.get('selling')}")
    print(f"- display: {product.get('display')}")
    print(f"- product_condition: {product.get('product_condition')}")
    print(f"- custom_product_code: {product.get('custom_product_code')}")
    
# 4. 변형 상품 확인 (혹시 몰라서)
print("\n4. 변형 상품 재확인...")
variants_url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products/{PRODUCT_NO}/variants"
response = requests.get(variants_url, headers=headers)
if response.status_code == 200:
    variants = response.json().get('variants', [])
    print(f"변형 상품 수: {len(variants)}")
    
    if variants:
        # 첫 번째 변형 상품 가격 수정 시도
        variant = variants[0]
        variant_code = variant.get('variant_code')
        print(f"- 변형 상품 코드: {variant_code}")
        print(f"- 현재 가격: {variant.get('price')}")
        
        # 변형 상품 가격 수정
        variant_url = f"{variants_url}/{variant_code}"
        variant_update = {
            "request": {
                "variant": {
                    "price": "13500"
                }
            }
        }
        
        response = requests.put(variant_url, headers=headers, json=variant_update)
        print(f"- 변형 상품 수정 응답: {response.status_code}")

print("\n=== 결론 ===")
print("API가 200 OK를 반환하지만 실제로 변경되지 않는 이유:")
print("1. Cafe24 API의 알려진 버그일 가능성")
print("2. 특정 상품 타입은 API로 수정 불가")
print("3. 캐시 문제 (변경은 되었지만 조회 시 이전 값)")
print("4. 권한은 있지만 다른 제약사항 존재")
print("\n최종 해결책: Cafe24 기술지원에 문의 필요")