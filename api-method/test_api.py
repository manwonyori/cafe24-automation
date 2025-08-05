#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 테스트 스크립트
"""
import requests
import json

# 로컬 테스트
base_url = "http://localhost:5000"

def test_api():
    print("=== API 테스트 시작 ===\n")
    
    # 1. 상태 확인
    print("1. API 상태 확인...")
    try:
        response = requests.get(f"{base_url}/api/status")
        print(f"Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 2. 상품 목록
    print("2. 상품 목록 조회...")
    try:
        response = requests.get(f"{base_url}/api/products?limit=5")
        print(f"Status: {response.status_code}")
        data = response.json()
        if data.get('success'):
            print(f"상품 수: {data.get('count', 0)}")
            print(f"첫 번째 상품: {data.get('products', [])[0] if data.get('products') else 'None'}")
        else:
            print(f"Error: {data.get('error')}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 3. 오늘 주문
    print("3. 오늘 주문 조회...")
    try:
        response = requests.get(f"{base_url}/api/orders/today")
        print(f"Status: {response.status_code}")
        data = response.json()
        if data.get('success'):
            print(f"주문 수: {data.get('count', 0)}")
            print(f"총 매출: ₩{data.get('total_amount', 0):,}")
        else:
            print(f"Error: {data.get('error')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()