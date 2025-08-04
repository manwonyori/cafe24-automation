#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
수정된 가격 확인
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

# 상품 정보 조회
url = f"https://{MALL_ID}.cafe24api.com/api/v2/admin/products/{PRODUCT_NO}"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    product = response.json().get('product', {})
    
    print("=== 현재 상품 정보 ===")
    print(f"상품명: {product.get('product_name')}")
    print(f"판매가: {product.get('price')}")
    
    # 마진율 계산
    selling_price = float(product.get('price', 0))
    # 공급가는 여러 필드명으로 시도
    supply_price = (float(product.get('supply_price') or 0) or 
                   float(product.get('cost_price') or 0) or
                   float(product.get('purchase_price') or 0))
    
    if supply_price > 0:
        margin_rate = ((selling_price - supply_price) / supply_price) * 100
        print(f"공급가: {supply_price:,.0f}")
        print(f"마진율: {margin_rate:.2f}%")
        
        if selling_price == 14800:
            print("\n✓ 가격 수정이 성공적으로 반영되었습니다!")
        else:
            print(f"\n⚠ 예상 가격(14,800원)과 다릅니다.")
    else:
        print("공급가 정보를 찾을 수 없습니다.")
        
else:
    print(f"상품 조회 실패: {response.status_code}")
    print(f"오류: {response.text}")