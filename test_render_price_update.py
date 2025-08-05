#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
"""
Render 웹 서비스에서 가격 수정 테스트
"""
import requests
import json
from datetime import datetime

# Render 웹 서비스 URL
RENDER_URL = "https://cafe24-automation.onrender.com"
PRODUCT_NO = 209
PRODUCT_NAME = "[인생]점보떡볶이1490g"
NEW_PRICE = 13500

print("=== Render 웹 서비스 가격 수정 테스트 ===\n")

# 1. API 상태 확인
print("1. Render 서비스 상태 확인...")
try:
    response = requests.get(f"{RENDER_URL}/api/status", timeout=10)
    print(f"- 상태 코드: {response.status_code}")
    if response.status_code == 200:
        status = response.json()
        print(f"- 서버 상태: {status.get('status')}")
        print(f"- 토큰 상태: {status.get('token_status', {}).get('valid')}")
except Exception as e:
    print(f"[ERROR] 연결 실패: {e}")

# 2. 제품 검색
print(f"\n2. 제품 검색: {PRODUCT_NAME}")
try:
    response = requests.get(f"{RENDER_URL}/api/products?limit=100", timeout=15)
    if response.status_code == 200:
        data = response.json()
        products = data.get('products', [])
        
        # 점보떡볶이 찾기
        found = False
        for product in products:
            if str(product.get('product_no')) == str(PRODUCT_NO):
                found = True
                print(f"✅ 제품 찾음!")
                print(f"- 상품코드: {product.get('product_no')}")
                print(f"- 상품명: {product.get('product_name')}")
                print(f"- 현재 가격: {product.get('price')}원")
                break
        
        if not found:
            print(f"❌ 상품코드 {PRODUCT_NO} 제품을 찾을 수 없습니다.")
except Exception as e:
    print(f"[ERROR] 제품 검색 실패: {e}")

# 3. 웹 대시보드 URL 안내
print("\n3. 웹 대시보드에서 가격 수정하기")
print("\n=== 웹에서 직접 수정하는 방법 ===")
print("\n[방법 1] 마진율 대시보드 사용:")
print(f"1. 접속: {RENDER_URL}/margin-dashboard")
print("2. 상품 목록에서 [인생]점보떡볶이1490g 찾기")
print("3. '가격수정' 버튼 클릭")
print(f"4. 새 가격 입력: {NEW_PRICE}원")

print("\n[방법 2] 가격 일괄 수정:")
print(f"1. 접속: {RENDER_URL}/margin-dashboard")
print("2. 상품 선택 (체크박스)")
print("3. '💰 가격 일괄 수정' 버튼 클릭")
print("4. 목표 마진율 또는 직접 가격 입력")

print("\n[방법 3] 엑셀 다운로드 후 업로드:")
print(f"1. 접속: {RENDER_URL}/margin-dashboard")
print("2. '📋 가격수정 엑셀 생성' 버튼 클릭")
print("3. 다운로드된 엑셀 파일에서 가격 수정")
print("4. Cafe24 관리자 페이지에서 업로드")

# 4. API 직접 호출 테스트
print("\n4. API 직접 가격 수정 시도...")
try:
    # PUT 요청으로 가격 수정
    update_url = f"{RENDER_URL}/api/products/{PRODUCT_NO}/price"
    update_data = {"price": str(NEW_PRICE)}
    
    response = requests.put(update_url, json=update_data, timeout=10)
    print(f"- 응답 코드: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ API 가격 수정 성공!")
        result = response.json()
        print(f"- 결과: {json.dumps(result, indent=2, ensure_ascii=False)}")
    elif response.status_code == 404:
        print("❌ API 엔드포인트가 구현되지 않았습니다.")
        print("웹 대시보드를 사용하거나 CSV 업로드 방식을 사용하세요.")
    else:
        print(f"❌ 실패: {response.text[:200]}")
except Exception as e:
    print(f"[ERROR] API 호출 실패: {e}")

# 5. 실제 사이트 확인
print("\n5. 실제 사이트 확인")
print(f"- 제품 페이지: https://manwonyori.com/product/detail.html?product_no={PRODUCT_NO}")
print("- 변경사항이 반영되는데 5-10분 걸릴 수 있습니다.")

print("\n=== 권장 사항 ===")
print("1. 웹 대시보드 사용을 권장합니다.")
print(f"2. 바로가기: {RENDER_URL}/margin-dashboard")
print("3. API가 작동하지 않으면 CSV 업로드 방식을 사용하세요.")
print("4. 모든 작업은 웹에서 직접 수행하세요.")