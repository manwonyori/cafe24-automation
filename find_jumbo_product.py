#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
점보떡볶이 제품 찾기
"""
import requests
import json

print("=== 점보떡볶이 제품 검색 ===\n")

# API로 제품 목록 가져오기 (최대 100개)
response = requests.get('http://localhost:5000/api/products?limit=100')

if response.status_code == 200:
    data = response.json()
    
    if isinstance(data, dict) and 'products' in data:
        products = data['products']
        print(f"총 제품 수: {len(products)}")
        
        # 모든 제품 이름 출력
        print("\n=== 전체 제품 목록 ===")
        for i, product in enumerate(products):
            product_name = product.get('product_name', '')
            product_no = product.get('product_no', '')
            price = product.get('price', 0)
            
            try:
                price_str = f"{int(price):,}" if price else "0"
            except:
                price_str = str(price)
            print(f"{i+1}. [{product_no}] {product_name} - {price_str}원")
            
            # 점보떡볶이 찾기
            if '점보' in product_name or '떡볶' in product_name or '1490' in product_name:
                print(f"\n★★★ 찾았습니다! ★★★")
                print(f"상품코드: {product_no}")
                print(f"상품명: {product_name}")
                print(f"현재가격: {price_str}원")
                
                # 이 정보를 파일로 저장
                found_product = {
                    "product_no": product_no,
                    "product_name": product_name,
                    "current_price": price,
                    "target_price": 13500
                }
                
                with open('jumbo_product_info.json', 'w', encoding='utf-8') as f:
                    json.dump(found_product, f, ensure_ascii=False, indent=2)
                
                print("\n정보가 jumbo_product_info.json에 저장되었습니다.")
    else:
        print("예상치 못한 응답 형식:")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
else:
    print(f"API 오류: {response.status_code}")
    print(response.text[:200])