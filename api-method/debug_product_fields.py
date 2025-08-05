#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
상품 필드 디버깅
"""
import requests
import json

# 토큰 읽기
with open('oauth_token.json', 'r', encoding='utf-8') as f:
    token_data = json.load(f)

MALL_ID = token_data['mall_id']
ACCESS_TOKEN = token_data['access_token']
PRODUCT_NO = 209

headers = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json',
    'X-Cafe24-Api-Version': '2025-06-01'
}

# 상품 정보 조회 (모든 필드)
url = f"https://{MALL_ID}.cafe24api.com/api/v2/admin/products/{PRODUCT_NO}"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    product = response.json().get('product', {})
    
    print("=== 모든 상품 필드 ===")
    for key, value in product.items():
        print(f"{key}: {value}")
        
    print("\n=== 가격 관련 필드만 ===")
    price_fields = ['price', 'supply_price', 'cost_price', 'purchase_price', 
                   'wholesale_price', 'retail_price', 'market_price']
    
    for field in price_fields:
        if field in product:
            print(f"{field}: {product[field]}")
else:
    print(f"상품 조회 실패: {response.status_code}")
    print(f"오류: {response.text}")