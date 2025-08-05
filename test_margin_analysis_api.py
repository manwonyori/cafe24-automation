#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
마진 분석 API 테스트
"""
import requests
import json
import sys
import io

# UTF-8 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Render 서버 URL
base_url = 'https://cafe24-automation.onrender.com'

print("=== 마진 분석 API 테스트 ===\n")

# 1. 마진 분석 API 호출
print("1. 마진 분석 API 호출:")
response = requests.get(f'{base_url}/api/margin/analysis')
print(f"상태 코드: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"✅ API 호출 성공!")
    
    # 전체 통계
    if 'statistics' in data:
        stats = data['statistics']
        print(f"\n전체 통계:")
        print(f"- 총 제품 수: {stats.get('total_products', 0)}")
        print(f"- 평균 마진율: {stats.get('average_margin', 0):.1f}%")
    
    # 제품 목록
    if 'products' in data:
        products = data['products']
        print(f"\n제품 목록: {len(products)}개")
        
        # 점보떡볶이 찾기
        found = False
        for product in products:
            product_name = product.get('product_name', '')
            if '점보떡볶' in product_name:
                found = True
                print(f"\n✅ [인생]점보떡볶이1490g 발견!")
                print(f"상품명: {product_name}")
                print(f"상품번호: {product.get('product_no')}")
                print(f"상품코드: {product.get('product_code')}")
                print(f"현재 판매가: {product.get('price', 0):,}원")
                print(f"공급가: {product.get('supply_price', 0):,}원")
                print(f"현재 마진율: {product.get('margin_rate', 0):.1f}%")
                print(f"마진액: {product.get('margin_amount', 0):,}원")
                
                # 13,500원으로 변경 시
                supply_price = product.get('supply_price', 0)
                if supply_price > 0:
                    new_margin_rate = ((13500 - supply_price) / 13500) * 100
                    new_margin_amount = 13500 - supply_price
                    
                    print(f"\n📊 13,500원으로 변경 시:")
                    print(f"예상 마진율: {new_margin_rate:.1f}%")
                    print(f"예상 마진액: {new_margin_amount:,}원")
                    print(f"마진율 변화: {new_margin_rate - product.get('margin_rate', 0):+.1f}%p")
                    
                    # 가격 수정 API 정보
                    product_no = product.get('product_no')
                    print(f"\n🔧 가격 수정 API:")
                    print(f"POST {base_url}/api/margin/update-prices")
                    print(f"Body: {{")
                    print(f'  "product_nos": ["{product_no}"],')
                    print(f'  "update_type": "price",')
                    print(f'  "price": 13500')
                    print(f"}}")
                break
        
        if not found:
            print("\n❌ 점보떡볶이 제품을 찾을 수 없습니다.")
            print("\n[인생] 브랜드 제품 목록:")
            count = 0
            for product in products:
                if '인생' in product.get('product_name', ''):
                    print(f"- {product.get('product_name')} ({product.get('price', 0):,}원)")
                    count += 1
                    if count >= 10:  # 처음 10개만 표시
                        break
else:
    print(f"❌ API 호출 실패")
    print(f"응답: {response.text[:200]}...")

print("\n\n=== 가격 수정 프로세스 ===")
print("1. 상품번호(product_no) 확인")
print("2. POST /api/margin/update-prices API 호출")
print("3. 또는 브라우저에서 마진 대시보드 사용")