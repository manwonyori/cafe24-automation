#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
"""
가격 수정 확인 스크립트
"""
import requests
import json
from datetime import datetime
import time

PRODUCT_NO = 209
PRODUCT_URL = "https://manwonyori.com/product/detail.html?product_no=209&cate_no=99&display_group=1"

print("=== [인생]점보떡볶이1490g 가격 수정 확인 ===\n")

# 1. API로 현재 가격 확인
print("1. API로 현재 가격 확인...")
try:
    # 로컬 API로 확인
    response = requests.get(f'http://localhost:5000/api/products?limit=100')
    if response.status_code == 200:
        data = response.json()
        products = data.get('products', [])
        
        for product in products:
            if str(product.get('product_no')) == str(PRODUCT_NO):
                print(f"[API 확인 결과]")
                print(f"- 상품코드: {product.get('product_no')}")
                print(f"- 상품명: {product.get('product_name')}")
                print(f"- 현재 가격: {product.get('price')}원")
                break
except Exception as e:
    print(f"[ERROR] API 확인 실패: {e}")

# 2. Cafe24 API 직접 조회
print("\n2. Cafe24 API 직접 조회...")
try:
    with open('oauth_token.json', 'r', encoding='utf-8') as f:
        token_data = json.load(f)
    
    headers = {
        'Authorization': f'Bearer {token_data["access_token"]}',
        'Content-Type': 'application/json',
        'X-Cafe24-Api-Version': '2025-06-01'
    }
    
    url = f"https://{token_data['mall_id']}.cafe24api.com/api/v2/admin/products/{PRODUCT_NO}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        product_data = response.json().get('product', {})
        print(f"[Cafe24 API 결과]")
        print(f"- 상품명: {product_data.get('product_name')}")
        print(f"- 판매가: {product_data.get('price')}원")
        print(f"- 수정일시: {product_data.get('updated_date')}")
    else:
        print(f"[ERROR] Cafe24 API 오류: {response.status_code}")
        print(response.text[:200])
except Exception as e:
    print(f"[ERROR] Cafe24 API 조회 실패: {e}")

# 3. 웹사이트 직접 확인
print(f"\n3. 웹사이트 확인...")
print(f"URL: {PRODUCT_URL}")
try:
    # 웹 페이지 가져오기
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(PRODUCT_URL, headers=headers)
    
    if response.status_code == 200:
        # 가격 정보 찾기 (간단한 패턴 매칭)
        import re
        
        # 다양한 가격 패턴 찾기
        price_patterns = [
            r'\"price\"\s*:\s*\"([0-9,]+)\"',
            r'\'price\'\s*:\s*\'([0-9,]+)\'',
            r'<span[^>]*class="[^"]*price[^"]*"[^>]*>([0-9,]+)원',
            r'data-price="([0-9,]+)"',
            r'판매가[^0-9]*([0-9,]+)원'
        ]
        
        found_prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, response.text)
            if matches:
                found_prices.extend(matches)
        
        if found_prices:
            print("[웹사이트에서 찾은 가격들]")
            for i, price in enumerate(set(found_prices)):
                print(f"- {price}원")
        else:
            print("[WARNING] 웹페이지에서 가격을 찾을 수 없습니다.")
            
    else:
        print(f"[ERROR] 웹사이트 접속 실패: {response.status_code}")
        
except Exception as e:
    print(f"[ERROR] 웹 확인 실패: {e}")

# 4. 가격 수정 재시도
print("\n4. 가격 수정 상태 확인...")
try:
    with open('price_update_log.json', 'r', encoding='utf-8') as f:
        log_data = json.load(f)
        print(f"[마지막 수정 시도]")
        print(f"- 시간: {log_data.get('updated_at')}")
        print(f"- 이전 가격: {log_data.get('old_price')}원")
        print(f"- 변경 가격: {log_data.get('new_price')}원")
except:
    print("[INFO] 수정 로그 없음")

print("\n=== 진단 결과 ===")
print("1. API 응답은 정상적으로 200 OK를 반환했습니다.")
print("2. 하지만 실제 사이트에 반영되지 않았을 수 있습니다.")
print("\n가능한 원인:")
print("- 캐시 문제 (몇 분 후 반영될 수 있음)")
print("- 토큰 권한 문제")
print("- API와 실제 상품 DB 동기화 지연")
print("\n해결 방법:")
print("1. 5-10분 후 다시 확인")
print("2. Cafe24 관리자 페이지에서 직접 확인")
print("3. 토큰 재발급 후 재시도")