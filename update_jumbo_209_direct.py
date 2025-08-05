#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
"""
[인생]점보떡볶이1490g (상품코드 209) 직접 가격 수정
"""
import requests
import json
from datetime import datetime

# 상품 정보
PRODUCT_NO = 209
PRODUCT_NAME = "[인생]점보떡볶이1490g"
CURRENT_PRICE = 12600
NEW_PRICE = 13500

print(f"=== {PRODUCT_NAME} 가격 수정 ===")
print(f"상품코드: {PRODUCT_NO}")
print(f"현재 가격: {CURRENT_PRICE:,}원")
print(f"변경할 가격: {NEW_PRICE:,}원\n")

# 방법 1: 로컬 API를 통한 수정 시도
print("1. 로컬 API를 통한 수정 시도...")
try:
    # PUT 요청으로 가격 수정
    update_url = f'http://localhost:5000/api/products/{PRODUCT_NO}'
    update_data = {
        "price": str(NEW_PRICE)
    }
    
    response = requests.put(update_url, json=update_data)
    print(f"응답 코드: {response.status_code}")
    
    if response.status_code == 200:
        print("[SUCCESS] 가격 수정 성공!")
    else:
        print(f"[FAIL] 실패: {response.text[:200]}")
except Exception as e:
    print(f"[ERROR] 오류: {e}")

# 방법 2: Cafe24 API 직접 호출
print("\n2. Cafe24 API 직접 호출 방법...")
try:
    with open('oauth_token.json', 'r', encoding='utf-8') as f:
        token_data = json.load(f)
    
    headers = {
        'Authorization': f'Bearer {token_data["access_token"]}',
        'Content-Type': 'application/json',
        'X-Cafe24-Api-Version': '2025-06-01'
    }
    
    update_data = {
        "request": {
            "product": {
                "price": str(NEW_PRICE)
            }
        }
    }
    
    url = f"https://{token_data['mall_id']}.cafe24api.com/api/v2/admin/products/{PRODUCT_NO}"
    
    print(f"URL: {url}")
    print(f"헤더: Bearer {token_data['access_token'][:20]}...")
    print(f"데이터: {json.dumps(update_data, indent=2)}")
    
    response = requests.put(url, headers=headers, json=update_data)
    print(f"\n응답 코드: {response.status_code}")
    
    if response.status_code == 200:
        print("[SUCCESS] 가격 수정 성공!")
        
        # 수정 정보 저장
        update_log = {
            "product_no": PRODUCT_NO,
            "product_name": PRODUCT_NAME,
            "old_price": CURRENT_PRICE,
            "new_price": NEW_PRICE,
            "updated_at": datetime.now().isoformat(),
            "method": "direct_api"
        }
        
        with open('price_update_log.json', 'w', encoding='utf-8') as f:
            json.dump(update_log, f, ensure_ascii=False, indent=2)
        
        print("수정 내역이 price_update_log.json에 저장되었습니다.")
    else:
        print(f"[FAIL] 실패: {response.text[:500]}")
        
except FileNotFoundError:
    print("[ERROR] oauth_token.json 파일이 없습니다.")
except Exception as e:
    print(f"[ERROR] 오류: {e}")

# 방법 3: CSV 업로드 방식
print("\n3. CSV 업로드 방식...")
print("CSV 파일 생성 중...")

import pandas as pd

# 최소한의 필드만 포함
csv_data = {
    '상품코드': [PRODUCT_NO],
    '판매가': [NEW_PRICE]
}

df = pd.DataFrame(csv_data)
csv_filename = f'price_update_{PRODUCT_NO}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
df.to_csv(csv_filename, index=False, encoding='utf-8-sig')

print(f"[SUCCESS] CSV 파일 생성 완료: {csv_filename}")
print("\n업로드 방법:")
print("1. Cafe24 관리자 로그인")
print("2. 상품관리 > 상품일괄등록/수정")
print("3. '상품일괄수정' 탭 선택")
print(f"4. {csv_filename} 파일 업로드")