#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
"""
웹 대시보드 CSV 업로드 API 테스트
"""
import requests
import os

# CSV 파일 경로
csv_file_path = "price_update_sample_jumbo.csv"

# 웹 서버 URL
base_url = "https://cafe24-automation.onrender.com"

print("=== CSV 업로드 API 테스트 ===\n")

# CSV 파일 확인
if not os.path.exists(csv_file_path):
    print(f"[ERROR] CSV 파일이 없습니다: {csv_file_path}")
    exit(1)

print(f"1. CSV 파일 확인: {csv_file_path}")
with open(csv_file_path, 'r', encoding='utf-8-sig') as f:
    content = f.read()
    print(f"파일 내용:\n{content}\n")

# API로 업로드
print("2. API로 업로드 시도...")
url = f"{base_url}/api/upload-price-csv"

with open(csv_file_path, 'rb') as f:
    files = {'file': (csv_file_path, f, 'text/csv')}
    
    try:
        response = requests.post(url, files=files, timeout=30)
        print(f"응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ 업로드 성공!")
            print(f"- 성공: {result.get('success_count', 0)}개")
            print(f"- 실패: {result.get('failed_count', 0)}개")
            
            if result.get('errors'):
                print("\n오류 내역:")
                for error in result['errors']:
                    print(f"  - {error}")
        else:
            print(f"\n❌ 업로드 실패")
            print(f"응답: {response.text}")
            
    except Exception as e:
        print(f"\n[ERROR] 요청 실패: {e}")

# 결과 확인
print("\n3. 가격 변경 확인...")
products_url = f"{base_url}/api/products?limit=100"
response = requests.get(products_url)

if response.status_code == 200:
    data = response.json()
    products = data.get('products', [])
    
    # 점보떡볶이 찾기
    for product in products:
        if product.get('product_no') == 209:
            print(f"\n[인생]점보떡볶이1490g")
            print(f"- 상품코드: {product.get('product_code')}")
            print(f"- 현재 가격: {product.get('price')}원")
            break

print("\n=== 테스트 완료 ===")
print("\n웹 대시보드에서 확인:")
print(f"- {base_url}/margin-dashboard")
print("- '📤 CSV 업로드로 가격 수정' 버튼으로 직접 업로드 가능")