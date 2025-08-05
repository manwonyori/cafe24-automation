#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
"""
가격 수정 디버깅 - 상세 분석
"""
import requests
import json
from datetime import datetime
import time

PRODUCT_NO = 209
NEW_PRICE = "13500"

print("=== 가격 수정 디버깅 ===\n")

# 토큰 읽기
try:
    with open('oauth_token.json', 'r', encoding='utf-8') as f:
        token_data = json.load(f)
except:
    print("[ERROR] oauth_token.json 파일 없음")
    exit(1)

headers = {
    'Authorization': f'Bearer {token_data["access_token"]}',
    'Content-Type': 'application/json',
    'X-Cafe24-Api-Version': '2025-06-01'
}

# 1. 현재 상품 정보 전체 조회
print("1. 현재 상품 정보 전체 조회...")
get_url = f"https://{token_data['mall_id']}.cafe24api.com/api/v2/admin/products/{PRODUCT_NO}"
response = requests.get(get_url, headers=headers)

if response.status_code == 200:
    product = response.json().get('product', {})
    print("[현재 상품 정보]")
    print(f"- product_no: {product.get('product_no')}")
    print(f"- product_name: {product.get('product_name')}")
    print(f"- price: {product.get('price')}")
    print(f"- retail_price: {product.get('retail_price')}")
    print(f"- supply_price: {product.get('supply_price')}")
    print(f"- display: {product.get('display')}")
    print(f"- selling: {product.get('selling')}")
    print(f"- updated_date: {product.get('updated_date')}")
    
    # 옵션 정보 확인
    if product.get('has_option'):
        print(f"- has_option: True")
        print("[WARNING] 옵션이 있는 상품은 가격 수정이 복잡할 수 있습니다.")
else:
    print(f"[ERROR] 상품 조회 실패: {response.status_code}")
    print(response.text)
    exit(1)

# 2. 다양한 방식으로 가격 수정 시도
print("\n2. 가격 수정 시도 (다양한 형식)...")

# 시도 1: 기본 형식
print("\n[시도 1] 기본 형식")
update_data1 = {
    "request": {
        "product": {
            "price": NEW_PRICE
        }
    }
}
response1 = requests.put(get_url, headers=headers, json=update_data1)
print(f"응답 코드: {response1.status_code}")
print(f"응답: {response1.text[:500]}")

# 시도 2: 숫자 형식
print("\n[시도 2] 숫자 형식")
update_data2 = {
    "request": {
        "product": {
            "price": 13500  # 문자열이 아닌 숫자
        }
    }
}
response2 = requests.put(get_url, headers=headers, json=update_data2)
print(f"응답 코드: {response2.status_code}")
print(f"응답: {response2.text[:500]}")

# 시도 3: retail_price도 함께 수정
print("\n[시도 3] retail_price도 함께 수정")
update_data3 = {
    "request": {
        "product": {
            "price": NEW_PRICE,
            "retail_price": NEW_PRICE
        }
    }
}
response3 = requests.put(get_url, headers=headers, json=update_data3)
print(f"응답 코드: {response3.status_code}")
print(f"응답: {response3.text[:500]}")

# 시도 4: 전체 필드 업데이트
print("\n[시도 4] 전체 가격 관련 필드")
update_data4 = {
    "request": {
        "product": {
            "price": NEW_PRICE,
            "retail_price": NEW_PRICE,
            "display": "T",
            "selling": "T"
        }
    }
}
response4 = requests.put(get_url, headers=headers, json=update_data4)
print(f"응답 코드: {response4.status_code}")
print(f"응답: {response4.text[:500]}")

# 3. 수정 후 확인
print("\n3. 수정 후 재확인...")
time.sleep(2)  # 2초 대기
response = requests.get(get_url, headers=headers)
if response.status_code == 200:
    updated_product = response.json().get('product', {})
    new_price = updated_product.get('price')
    print(f"[수정 후 가격]")
    print(f"- price: {new_price}")
    print(f"- retail_price: {updated_product.get('retail_price')}")
    
    if str(new_price) == NEW_PRICE:
        print("\n[SUCCESS] 가격이 성공적으로 변경되었습니다!")
    else:
        print(f"\n[FAIL] 가격이 변경되지 않았습니다. (현재: {new_price}, 목표: {NEW_PRICE})")
        
# 4. 토큰 권한 확인
print("\n4. 토큰 권한 확인...")
scope_url = f"https://{token_data['mall_id']}.cafe24api.com/api/v2/oauth/me"
response = requests.get(scope_url, headers=headers)
if response.status_code == 200:
    scope_data = response.json()
    print(f"[토큰 정보]")
    print(f"- scopes: {scope_data.get('scopes', [])}")
    if 'mall.write_product' in scope_data.get('scopes', []):
        print("- [OK] 상품 수정 권한 있음")
    else:
        print("- [WARNING] 상품 수정 권한 없을 수 있음")

print("\n=== 분석 완료 ===")