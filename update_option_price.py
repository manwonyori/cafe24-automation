#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
"""
옵션이 있는 상품의 가격 수정
"""
import requests
import json

PRODUCT_NO = 209
NEW_PRICE = "13500"

print("=== 옵션 상품 가격 수정 ===\n")

# 토큰 읽기
with open('oauth_token.json', 'r', encoding='utf-8') as f:
    token_data = json.load(f)

headers = {
    'Authorization': f'Bearer {token_data["access_token"]}',
    'Content-Type': 'application/json',
    'X-Cafe24-Api-Version': '2025-06-01'
}

mall_id = token_data['mall_id']

# 1. 옵션 정보 조회
print("1. 상품 옵션 정보 조회...")
option_url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products/{PRODUCT_NO}/options"
response = requests.get(option_url, headers=headers)

if response.status_code == 200:
    options_data = response.json()
    options = options_data.get('options', [])
    
    print(f"[옵션 정보]")
    print(f"- 옵션 개수: {len(options)}")
    
    for i, option in enumerate(options[:5]):  # 처음 5개만 표시
        print(f"\n옵션 {i+1}:")
        print(f"- option_code: {option.get('option_code')}")
        print(f"- option_value: {option.get('option_value')}")
        print(f"- option_price: {option.get('option_price')}")
        print(f"- use_option: {option.get('use_option')}")
else:
    print(f"[ERROR] 옵션 조회 실패: {response.status_code}")

# 2. 변형 상품(variants) 조회
print("\n\n2. 변형 상품(Variants) 조회...")
variants_url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products/{PRODUCT_NO}/variants"
response = requests.get(variants_url, headers=headers)

if response.status_code == 200:
    variants_data = response.json()
    variants = variants_data.get('variants', [])
    
    print(f"[변형 상품 정보]")
    print(f"- 변형 상품 개수: {len(variants)}")
    
    # 모든 변형 상품 ID 수집
    variant_codes = []
    for i, variant in enumerate(variants):
        variant_code = variant.get('variant_code')
        variant_codes.append(variant_code)
        
        if i < 3:  # 처음 3개만 표시
            print(f"\n변형 상품 {i+1}:")
            print(f"- variant_code: {variant_code}")
            print(f"- option_value: {variant.get('option_value')}")
            print(f"- price: {variant.get('price')}")
            print(f"- quantity: {variant.get('quantity')}")
    
    # 3. 변형 상품 가격 일괄 수정
    if variant_codes:
        print(f"\n\n3. 변형 상품 가격 일괄 수정 시도...")
        print(f"- 수정할 변형 상품 수: {len(variant_codes)}")
        
        # 각 변형 상품 가격 수정
        success_count = 0
        for variant_code in variant_codes:
            variant_url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products/{PRODUCT_NO}/variants/{variant_code}"
            
            update_data = {
                "request": {
                    "variant": {
                        "price": NEW_PRICE
                    }
                }
            }
            
            response = requests.put(variant_url, headers=headers, json=update_data)
            if response.status_code == 200:
                success_count += 1
                print(f".", end="", flush=True)
            else:
                print(f"\n[ERROR] {variant_code} 수정 실패: {response.status_code}")
                print(response.text[:200])
                break
        
        print(f"\n\n[결과] {success_count}/{len(variant_codes)} 변형 상품 가격 수정 완료")
        
        # 4. 기본 상품 가격도 수정
        print("\n4. 기본 상품 가격 수정...")
        product_url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products/{PRODUCT_NO}"
        update_data = {
            "request": {
                "product": {
                    "price": NEW_PRICE,
                    "retail_price": NEW_PRICE
                }
            }
        }
        
        response = requests.put(product_url, headers=headers, json=update_data)
        if response.status_code == 200:
            print("[SUCCESS] 기본 상품 가격 수정 완료")
        else:
            print(f"[ERROR] 기본 상품 가격 수정 실패: {response.status_code}")
        
        # 5. 최종 확인
        print("\n5. 최종 가격 확인...")
        response = requests.get(product_url, headers=headers)
        if response.status_code == 200:
            product = response.json().get('product', {})
            print(f"- 기본 상품 가격: {product.get('price')}")
            
            # 첫 번째 변형 상품 확인
            if variant_codes:
                variant_url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products/{PRODUCT_NO}/variants/{variant_codes[0]}"
                response = requests.get(variant_url, headers=headers)
                if response.status_code == 200:
                    variant = response.json().get('variant', {})
                    print(f"- 변형 상품 가격: {variant.get('price')}")
else:
    print(f"[ERROR] 변형 상품 조회 실패: {response.status_code}")
    print(response.text[:500])

print("\n=== 완료 ===")
print("\n[참고]")
print("- 옵션이 있는 상품은 각 변형 상품(variant)의 가격을 개별적으로 수정해야 합니다.")
print("- 사이트에 반영되는데 시간이 걸릴 수 있습니다.")
print("- Cafe24 관리자 페이지에서 확인해보세요.")