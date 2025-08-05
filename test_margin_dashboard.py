#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
마진 대시보드 API 테스트
"""
import requests
import json
import sys
import io

# UTF-8 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# API 서버 URL
base_url = 'https://cafe24-automation.onrender.com'

print("=== 마진 대시보드 관련 API 테스트 ===\n")

# 1. 마진 프리뷰 API 테스트
print("1. 마진 프리뷰 API 테스트:")
response = requests.get(f'{base_url}/api/margin/preview')
print(f"상태 코드: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"총 제품 수: {data.get('total_products', 0)}")
    
    # 제품 목록에서 점보떡볶이 찾기
    products = data.get('products', [])
    print(f"\n제품 목록 (처음 10개):")
    
    for i, product in enumerate(products[:10]):
        print(f"{i+1}. {product.get('product_name')} - {product.get('price', 0):,}원")
        
    # 점보떡볶이 검색
    print("\n점보떡볶이 검색 중...")
    found = False
    for product in products:
        if '점보떡볶' in str(product.get('product_name', '')):
            found = True
            print(f"\n✅ 제품 발견!")
            print(f"상품명: {product.get('product_name')}")
            print(f"상품코드: {product.get('product_code')}")
            print(f"현재 판매가: {product.get('price', 0):,}원")
            print(f"공급가: {product.get('supply_price', 0):,}원")
            print(f"마진율: {product.get('margin_rate', 0):.1f}%")
            
            # 가격 변경 시뮬레이션
            new_price = 13500
            supply_price = product.get('supply_price', 0)
            if supply_price > 0:
                new_margin = ((new_price - supply_price) / new_price) * 100
                print(f"\n📊 13,500원으로 변경 시:")
                print(f"예상 마진율: {new_margin:.1f}%")
                print(f"마진율 변화: {new_margin - product.get('margin_rate', 0):+.1f}%p")
    
    if not found:
        print("❌ 점보떡볶이 제품을 찾을 수 없습니다.")
        
        # 전체 제품명 출력
        print("\n전체 제품 목록:")
        for product in products:
            if '인생' in str(product.get('product_name', '')):
                print(f"- {product.get('product_name')}")

# 2. 가격 수정 API 테스트 준비
print("\n\n2. 가격 수정 API 정보:")
print("- 엔드포인트: POST /api/products/{product_no}/price")
print("- 필요 데이터: price(판매가) 또는 supply_price(공급가)")
print("- 마진 대시보드에서 제품 선택 후 '가격 수정' 버튼으로 수정 가능")