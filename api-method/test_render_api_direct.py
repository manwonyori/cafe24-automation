#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render 서버 API 직접 테스트
"""
import requests
import json
import sys
import io

# UTF-8 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Render 서버 URL
base_url = 'https://cafe24-automation.onrender.com'

print("=== Render 서버 API 테스트 ===\n")

# 1. 서버 상태 확인
print("1. 서버 상태 확인:")
response = requests.get(f'{base_url}/')
print(f"상태 코드: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"서버 상태: {data.get('status')}")
    print(f"버전: {data.get('version')}")

# 2. 자연어 명령으로 제품 검색
print("\n2. 자연어 명령으로 제품 검색:")
commands = [
    "전체 상품 보여줘",
    "점보떡볶이 상품",
    "인생 브랜드 상품"
]

for cmd in commands:
    print(f"\n명령: '{cmd}'")
    try:
        response = requests.post(
            f'{base_url}/api/execute',
            json={"command": cmd},
            headers={'Content-Type': 'application/json'}
        )
        print(f"상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'data' in result and isinstance(result['data'], list):
                products = result['data']
                print(f"검색 결과: {len(products)}개 제품")
                
                # 점보떡볶이 찾기
                for product in products:
                    if '점보떡볶' in str(product.get('product_name', '')):
                        print(f"\n✅ 찾았습니다!")
                        print(f"상품명: {product.get('product_name')}")
                        print(f"상품번호: {product.get('product_no')}")
                        print(f"현재 가격: {product.get('price', 0):,}원")
                        print(f"공급가: {product.get('supply_price', 0):,}원")
                        
                        # 마진율 계산
                        price = product.get('price', 0)
                        supply_price = product.get('supply_price', 0)
                        if price > 0 and supply_price > 0:
                            margin = ((price - supply_price) / price) * 100
                            print(f"현재 마진율: {margin:.1f}%")
                            
                            # 13,500원으로 변경 시
                            new_margin = ((13500 - supply_price) / 13500) * 100
                            print(f"\n13,500원 변경 시:")
                            print(f"예상 마진율: {new_margin:.1f}%")
                            print(f"마진율 변화: {new_margin - margin:+.1f}%p")
            else:
                print(f"응답: {result.get('message', 'No data')}")
    except Exception as e:
        print(f"오류: {str(e)}")

# 3. 가격 수정 방법 안내
print("\n\n=== 가격 수정 방법 ===")
print("1. 브라우저에서 https://cafe24-automation.onrender.com/margin-dashboard 접속")
print("2. 제품 검색란에 '점보떡볶이' 입력")
print("3. [인생]점보떡볶이1490g 제품의 '가격 수정' 버튼 클릭")
print("4. 13,500원 입력 후 저장")
print("\n또는 API 직접 호출:")
print("POST /api/products/{product_no}/price")
print("Body: {\"price\": 13500}")