#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
"""
API 권한 문제 심층 분석
"""
import requests
import json

print("=== API 권한 및 가격 수정 문제 디버깅 ===\n")

# 토큰 읽기
with open('oauth_token.json', 'r', encoding='utf-8') as f:
    token_data = json.load(f)

headers = {
    'Authorization': f'Bearer {token_data["access_token"]}',
    'Content-Type': 'application/json',
    'X-Cafe24-Api-Version': '2025-06-01'
}

mall_id = token_data['mall_id']
PRODUCT_NO = 209

# 1. 토큰 권한 확인
print("1. OAuth 토큰 권한 확인...")
url = f"https://{mall_id}.cafe24api.com/api/v2/oauth/me"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print(f"- Client ID: {data.get('client_id')}")
    print(f"- Mall ID: {data.get('mall_id')}")
    print(f"- User ID: {data.get('user_id')}")
    print(f"- Scopes: {data.get('scopes', [])}")
    
    if 'mall.write_product' in data.get('scopes', []):
        print("✅ mall.write_product 권한 있음")

# 2. 상품 정보 상세 조회
print(f"\n2. 상품 {PRODUCT_NO} 상세 정보...")
product_url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products/{PRODUCT_NO}"
response = requests.get(product_url, headers=headers)

if response.status_code == 200:
    product = response.json().get('product', {})
    print(f"- product_no: {product.get('product_no')}")
    print(f"- product_code: {product.get('product_code')}")
    print(f"- has_option: {product.get('has_option')}")
    print(f"- use_option: {product.get('use_option')}")
    print(f"- option_type: {product.get('option_type')}")
    print(f"- price: {product.get('price')}")
    print(f"- price_content: {product.get('price_content')}")
    print(f"- price_calculating_unit: {product.get('price_calculating_unit')}")

# 3. 다양한 가격 수정 시도
print("\n3. 다양한 가격 수정 방법 테스트...")

# 시도 1: 옵션 사용 안함으로 변경 후 가격 수정
print("\n[시도 1] 옵션 사용 안함으로 변경")
update_data = {
    "request": {
        "product": {
            "has_option": "F",
            "price": "13500"
        }
    }
}
response = requests.put(product_url, headers=headers, json=update_data)
print(f"응답: {response.status_code} - {response.text[:200]}")

# 시도 2: 가격 관련 모든 필드 수정
print("\n[시도 2] 모든 가격 필드 수정")
update_data = {
    "request": {
        "product": {
            "price": "13500",
            "retail_price": "13500",
            "supply_price": "11000",
            "price_content": "13500"
        }
    }
}
response = requests.put(product_url, headers=headers, json=update_data)
print(f"응답: {response.status_code} - {response.text[:200]}")

# 시도 3: 필드별 개별 수정
print("\n[시도 3] price 필드만 수정")
update_data = {
    "request": {
        "product": {
            "price": "13500"
        }
    }
}
response = requests.put(product_url, headers=headers, json=update_data)
print(f"응답: {response.status_code}")

# 바로 다시 조회
response = requests.get(product_url, headers=headers)
if response.status_code == 200:
    updated_price = response.json().get('product', {}).get('price')
    print(f"수정 후 가격: {updated_price}")
    
    if updated_price == "13500" or updated_price == "13500.00":
        print("✅ 가격 수정 성공!")
    else:
        print("❌ 가격 수정 실패")

# 4. API 제한사항 확인
print("\n4. 가능한 원인 분석...")
print("- 옵션 상품은 기본 가격 수정 불가능")
print("- 변형 상품(variants)의 가격을 개별 수정해야 함")
print("- API 버전에 따른 제한")
print("- 상품 상태에 따른 제한 (판매중, 품절 등)")

# 5. 대안 제시
print("\n5. 해결 방법:")
print("1) 변형 상품 API 사용 (/products/{id}/variants)")
print("2) 상품 옵션 제거 후 가격 수정")
print("3) Cafe24에 문의하여 API 제한사항 확인")
print("4) 다른 API 버전 시도 (2024-03-01 등)")