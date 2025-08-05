#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
점보떡볶이 제품 가격 확인
"""
import requests
import json
import sys
import io

# UTF-8 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# API 서버 URL - Render 실제 서버
base_url = 'https://cafe24-automation.onrender.com'

# 제품 검색
print("=== [인생]점보떡볶이1490g 제품 검색 중... ===\n")

response = requests.get(f'{base_url}/api/products')
if response.status_code == 200:
    products = response.json()
    found = False
    
    # [인생]점보떡볶이 찾기
    for product in products:
        product_name = product.get('product_name', '')
        if '점보떡볶' in product_name and '1490' in product_name:
            found = True
            print(f"✅ 제품 발견!")
            print(f"상품명: {product_name}")
            print(f"상품코드: {product.get('product_code')}")
            print(f"현재 판매가: {product.get('price', 0):,}원")
            print(f"공급가: {product.get('supply_price', 0):,}원")
            print(f"마진율: {product.get('margin_rate', 0):.1f}%")
            print(f"재고: {product.get('stock_quantity', 0)}개")
            print('-' * 50)
            
            # 13,500원으로 변경 시 마진율 계산
            new_price = 13500
            supply_price = product.get('supply_price', 0)
            if supply_price > 0:
                new_margin = ((new_price - supply_price) / new_price) * 100
                print(f"\n📊 가격 변경 시뮬레이션:")
                print(f"변경 후 판매가: {new_price:,}원")
                print(f"변경 후 마진율: {new_margin:.1f}%")
                print(f"마진율 변화: {new_margin - product.get('margin_rate', 0):+.1f}%p")
    
    if not found:
        print("❌ [인생]점보떡볶이1490g 제품을 찾을 수 없습니다.")
        print("\n전체 제품 목록:")
        for product in products[:10]:  # 처음 10개만 표시
            print(f"- {product.get('product_name')}")
else:
    print(f"❌ API 요청 실패: {response.status_code}")