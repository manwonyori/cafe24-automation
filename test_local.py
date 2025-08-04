#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
로컬에서 카페24 API 테스트
"""

import os
import sys
import json
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv('config/.env')

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cafe24_system import Cafe24System

def test_local():
    print("=== 카페24 API 로컬 테스트 ===\n")
    
    # 환경 변수 확인
    print("1. 환경 변수 확인:")
    mall_id = os.getenv('CAFE24_MALL_ID')
    client_id = os.getenv('CAFE24_CLIENT_ID')
    print(f"   Mall ID: {mall_id}")
    print(f"   Client ID: {client_id[:10]}...")
    
    # 시스템 초기화
    print("\n2. 시스템 초기화:")
    try:
        system = Cafe24System()
        mode = "Production" if not system.demo_mode else "Demo"
        print(f"   시스템 모드: {mode}")
    except Exception as e:
        print(f"   오류: {e}")
        return
    
    # API 테스트
    print("\n3. API 테스트:")
    
    # 상품 조회
    print("   - 상품 조회 중...")
    try:
        products = system.get_products(limit=3)
        print(f"     ✓ 상품 {len(products)}개 조회 성공")
        for i, product in enumerate(products[:3], 1):
            print(f"       {i}. {product.get('product_name', 'Unknown')}")
    except Exception as e:
        print(f"     ✗ 상품 조회 실패: {e}")
    
    # 자연어 명령
    print("\n   - 자연어 명령 테스트...")
    commands = ["상품 목록 보여줘", "재고 부족 상품"]
    for cmd in commands:
        try:
            result = system.execute(cmd)
            status = "✓" if result['success'] else "✗"
            print(f"     {status} '{cmd}'")
        except Exception as e:
            print(f"     ✗ '{cmd}' 실행 실패: {e}")
    
    print("\n=== 테스트 완료 ===")

if __name__ == "__main__":
    test_local()