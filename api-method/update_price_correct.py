#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
올바른 형식으로 가격 수정
"""
import requests
import json

# 토큰 읽기
with open('oauth_token.json', 'r', encoding='utf-8') as f:
    token_data = json.load(f)

MALL_ID = token_data['mall_id']
ACCESS_TOKEN = token_data['access_token']
PRODUCT_NO = 209
NEW_PRICE = 14800

headers = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json',
    'X-Cafe24-Api-Version': '2025-06-01'
}

# 정확한 업데이트 데이터 형식
update_data = {
    "request": {
        "product": {
            "shop_no": 1,
            "product_no": PRODUCT_NO,
            "price": NEW_PRICE  # 숫자로 전송
        }
    }
}

print(f"=== 가격 수정 재시도 ===")
print(f"상품번호: {PRODUCT_NO}")
print(f"새 가격: {NEW_PRICE:,}원")
print(f"요청 데이터: {json.dumps(update_data, indent=2)}")

url = f"https://{MALL_ID}.cafe24api.com/api/v2/admin/products/{PRODUCT_NO}"
response = requests.put(url, headers=headers, json=update_data)

print(f"\n응답 코드: {response.status_code}")
print(f"응답 내용: {response.text}")

if response.status_code == 200:
    print("\n가격 수정 API 호출 완료")
    
    # 즉시 재확인
    print("\n=== 업데이트된 가격 확인 ===")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        product = response.json().get('product', {})
        current_price = float(product.get('price', 0))
        print(f"현재 가격: {current_price:,.0f}원")
        
        if current_price == NEW_PRICE:
            print("SUCCESS: 가격이 성공적으로 업데이트되었습니다!")
            
            # 복구 정보 저장
            restore_info = {
                "product_no": PRODUCT_NO,
                "product_name": product.get('product_name'),
                "original_price": 12600,
                "updated_price": NEW_PRICE,
                "test_success": True
            }
            
            with open('restore_info.json', 'w', encoding='utf-8') as f:
                json.dump(restore_info, f, ensure_ascii=False, indent=2)
                
            print("복구 정보가 restore_info.json에 저장되었습니다.")
        else:
            print(f"FAILED: 가격이 업데이트되지 않았습니다.")
else:
    print("가격 수정 실패")