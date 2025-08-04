#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[인생]점보떡볶1490g 가격 수정 테스트
"""
import requests
import json

# 상품 정보
PRODUCT_NO = 209
PRODUCT_NAME = "[인생]점보떡볶1490g"
ORIGINAL_PRICE = 12600
NEW_PRICE = 14800
TARGET_MARGIN = 34.29

# API 엔드포인트
API_URL = "https://cafe24-automation.onrender.com/api/margin/update-prices"

# 1. 가격 수정 요청
print(f"=== {PRODUCT_NAME} 가격 수정 테스트 ===")
print(f"상품번호: {PRODUCT_NO}")
print(f"현재 가격: {ORIGINAL_PRICE:,}원")
print(f"변경 가격: {NEW_PRICE:,}원")
print(f"목표 마진율: {TARGET_MARGIN}%")
print("-" * 50)

update_data = {
    "product_nos": [PRODUCT_NO],
    "target_margin": TARGET_MARGIN,
    "update_type": "selling"  # 판매가 수정
}

print("\n1. 가격 수정 요청 중...")
response = requests.post(API_URL, json=update_data)
print(f"응답 코드: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    print(f"수정 결과: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if result.get('success'):
        print(f"\n✅ 가격 수정 성공!")
        print(f"성공: {result.get('success_count', 0)}개")
        print(f"실패: {result.get('failed_count', 0)}개")
        
        # 결과 상세 확인
        if 'results' in result:
            for item in result['results']:
                if item.get('status') == 'success':
                    print(f"\n상품명: {item.get('product_name')}")
                    print(f"이전 가격: {item.get('old_price'):,}원")
                    print(f"새 가격: {item.get('new_price'):,}원")
else:
    print(f"❌ 가격 수정 실패: {response.text}")

print("\n" + "=" * 50)
print("테스트 완료! 원래 가격으로 복구하려면 restore_price.py를 실행하세요.")