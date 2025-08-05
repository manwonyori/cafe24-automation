#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
직접 Cafe24 API로 가격 수정
"""
import requests
import json
from datetime import datetime

# 토큰 읽기
with open('oauth_token.json', 'r', encoding='utf-8') as f:
    token_data = json.load(f)

# API 설정
MALL_ID = token_data['mall_id']
ACCESS_TOKEN = token_data['access_token']
PRODUCT_NO = 209
NEW_PRICE = 14800

# 1. 현재 상품 정보 조회
headers = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json',
    'X-Cafe24-Api-Version': '2025-06-01'
}

# 상품 정보 조회
get_url = f"https://{MALL_ID}.cafe24api.com/api/v2/admin/products/{PRODUCT_NO}"
print(f"1. 현재 상품 정보 조회 중...")
response = requests.get(get_url, headers=headers)

if response.status_code == 200:
    product_data = response.json().get('product', {})
    current_price = product_data.get('price')
    product_name = product_data.get('product_name')
    
    print(f"\n현재 상품 정보:")
    print(f"- 상품명: {product_name}")
    print(f"- 현재 가격: {current_price}")
    print(f"- 변경할 가격: {NEW_PRICE}")
    
    # 2. 가격 수정
    update_data = {
        "request": {
            "product": {
                "price": str(NEW_PRICE)
            }
        }
    }
    
    print(f"\n2. 가격 수정 요청 중...")
    print(f"요청 데이터: {json.dumps(update_data, indent=2)}")
    
    put_url = f"https://{MALL_ID}.cafe24api.com/api/v2/admin/products/{PRODUCT_NO}"
    response = requests.put(put_url, headers=headers, json=update_data)
    
    print(f"\n응답 코드: {response.status_code}")
    print(f"응답 내용: {response.text[:500]}")
    
    if response.status_code == 200:
        print(f"\n✓ 가격 수정 성공!")
        
        # 3. 수정된 가격 확인
        print(f"\n3. 수정된 가격 확인 중...")
        response = requests.get(get_url, headers=headers)
        if response.status_code == 200:
            new_product_data = response.json().get('product', {})
            updated_price = new_product_data.get('price')
            print(f"- 수정된 가격: {updated_price}")
            
            # 복구 정보 저장
            restore_info = {
                "product_no": PRODUCT_NO,
                "product_name": product_name,
                "original_price": current_price,
                "test_price": NEW_PRICE,
                "test_time": datetime.now().isoformat()
            }
            
            with open('restore_price_info.json', 'w', encoding='utf-8') as f:
                json.dump(restore_info, f, ensure_ascii=False, indent=2)
            
            print(f"\n복구 정보가 restore_price_info.json에 저장되었습니다.")
    else:
        print(f"\n× 가격 수정 실패")
else:
    print(f"상품 조회 실패: {response.status_code}")