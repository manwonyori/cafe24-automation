#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[인생]점보떡볶이1490g API 직접 가격 수정
"""
import requests
import json
import sys
import io

# UTF-8 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def update_price_local():
    """로컬 서버를 통한 가격 수정"""
    base_url = 'http://localhost:5000'
    
    print("=== API를 통한 직접 가격 수정 ===\n")
    
    # 1. 먼저 제품 찾기
    print("1. 제품 검색 중...")
    
    # 제품 목록 가져오기 (limit 파라미터 추가)
    try:
        response = requests.get(f'{base_url}/api/products?limit=100')
        if response.status_code == 200:
            products = response.json()
            
            # 점보떡볶이 찾기
            target_product = None
            for product in products:
                product_name = str(product.get('product_name', ''))
                if '점보떡볶' in product_name and '1490' in product_name:
                    target_product = product
                    print(f"\n✅ 제품 찾음!")
                    print(f"- 상품코드: {product.get('product_no')}")
                    print(f"- 상품명: {product_name}")
                    print(f"- 현재 가격: {product.get('price', 0):,}원")
                    break
            
            if not target_product:
                print("❌ 점보떡볶이 제품을 찾을 수 없습니다.")
                return
            
            # 2. 가격 수정 API 호출
            product_no = target_product.get('product_no')
            if not product_no:
                print("❌ 상품코드가 없습니다.")
                return
            
            print(f"\n2. 가격을 13,500원으로 수정 중...")
            
            # PUT 요청으로 가격 수정
            update_data = {
                "price": "13500",
                "product_no": product_no
            }
            
            response = requests.put(
                f'{base_url}/api/products/{product_no}/price',
                json=update_data
            )
            
            if response.status_code == 200:
                print("✅ 가격 수정 성공!")
                result = response.json()
                print(f"응답: {json.dumps(result, indent=2, ensure_ascii=False)}")
            else:
                print(f"❌ 가격 수정 실패: {response.status_code}")
                print(f"응답: {response.text}")
                
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def update_price_direct():
    """Cafe24 API 직접 호출"""
    print("\n=== Cafe24 API 직접 호출 방법 ===")
    
    # oauth_token.json 파일 읽기
    try:
        with open('oauth_token.json', 'r', encoding='utf-8') as f:
            token_data = json.load(f)
        
        print("\n직접 API 호출 코드:")
        print(f"""
import requests
import json

# 토큰 정보
MALL_ID = "{token_data.get('mall_id', 'manwonyori')}"
ACCESS_TOKEN = "{token_data.get('access_token', 'YOUR_TOKEN')[:20]}..."
PRODUCT_NO = "점보떡볶이 상품코드"  # 실제 상품코드로 교체

# API 호출
headers = {{
    'Authorization': f'Bearer {{ACCESS_TOKEN}}',
    'Content-Type': 'application/json',
    'X-Cafe24-Api-Version': '2025-06-01'
}}

# 가격 수정
update_data = {{
    "request": {{
        "product": {{
            "price": "13500"
        }}
    }}
}}

url = f"https://{{MALL_ID}}.cafe24api.com/api/v2/admin/products/{{PRODUCT_NO}}"
response = requests.put(url, headers=headers, json=update_data)

if response.status_code == 200:
    print("✅ 가격 수정 성공!")
else:
    print(f"❌ 실패: {{response.status_code}}")
""")
        
    except FileNotFoundError:
        print("❌ oauth_token.json 파일이 없습니다.")
        print("토큰 파일을 먼저 생성해주세요.")

if __name__ == "__main__":
    # 로컬 서버 API 시도
    update_price_local()
    
    # 직접 API 호출 방법 안내
    update_price_direct()