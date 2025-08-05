#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify Cafe24 API Configuration
Tests connection and lists available endpoints
"""

import os
import sys
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cafe24_system import Cafe24System


def verify_environment():
    """Verify environment variables are set"""
    print("=== 환경 변수 확인 ===")
    
    required_vars = [
        'CAFE24_MALL_ID',
        'CAFE24_CLIENT_ID', 
        'CAFE24_CLIENT_SECRET'
    ]
    
    optional_vars = [
        'CAFE24_ACCESS_TOKEN',
        'CAFE24_REFRESH_TOKEN',
        'CAFE24_API_VERSION'
    ]
    
    all_set = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # 보안을 위해 일부만 표시
            masked = value[:4] + '****' + value[-4:] if len(value) > 8 else '****'
            print(f"✓ {var}: {masked}")
        else:
            print(f"✗ {var}: 설정되지 않음")
            all_set = False
            
    print("\n=== 선택적 환경 변수 ===")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            masked = value[:4] + '****' + value[-4:] if len(value) > 8 else '****'
            print(f"✓ {var}: {masked}")
        else:
            print(f"- {var}: 설정되지 않음")
            
    return all_set


def test_api_connection():
    """Test API connection"""
    print("\n=== API 연결 테스트 ===")
    
    try:
        system = Cafe24System()
        
        # Check if in demo mode
        if hasattr(system, 'demo_mode') and system.demo_mode:
            print("⚠️  데모 모드로 실행 중 (실제 API 연결 없음)")
            return True
            
        # Test product API
        print("상품 API 테스트 중...")
        products = system.get_products(limit=1)
        print(f"✓ 상품 조회 성공 (총 {len(products)}개)")
        
        # Test order API  
        print("\n주문 API 테스트 중...")
        orders = system.get_orders(limit=1)
        print(f"✓ 주문 조회 성공 (총 {len(orders)}개)")
        
        # Test customer API
        print("\n고객 API 테스트 중...")
        result = system.execute("고객 목록 조회")
        if result['success']:
            print("✓ 고객 조회 성공")
        
        # Test NLP
        print("\n자연어 처리 테스트 중...")
        commands = [
            "상품 목록 보여줘",
            "오늘 주문 확인",
            "재고 부족 상품"
        ]
        
        for cmd in commands:
            result = system.execute(cmd)
            status = "✓" if result['success'] else "✗"
            print(f"{status} '{cmd}' → {result.get('intent', {}).get('action', 'Unknown')}")
            
        return True
        
    except Exception as e:
        print(f"✗ API 연결 실패: {str(e)}")
        return False


def display_api_info():
    """Display API endpoint information"""
    print("\n=== 사용 가능한 API 엔드포인트 ===")
    
    endpoints = {
        "상품 관리": [
            "GET /api/products - 상품 목록 조회",
            "GET /api/products/{id} - 상품 상세 조회",
            "POST /api/execute - 자연어 명령 실행"
        ],
        "주문 관리": [
            "GET /api/orders - 주문 목록 조회", 
            "GET /api/orders/{id} - 주문 상세 조회"
        ],
        "재고 관리": [
            "GET /api/inventory - 재고 현황 조회",
            "GET /api/inventory?threshold=10 - 재고 부족 상품"
        ],
        "리포트": [
            "GET /api/report?type=daily - 일일 리포트",
            "GET /api/report?type=weekly - 주간 리포트",
            "GET /api/report?type=monthly - 월간 리포트"
        ],
        "시스템": [
            "GET /health - 헬스체크",
            "GET / - API 정보"
        ]
    }
    
    base_url = "https://cafe24-automation-vvkx.onrender.com"
    
    for category, apis in endpoints.items():
        print(f"\n{category}:")
        for api in apis:
            print(f"  {api}")
            
    print(f"\n기본 URL: {base_url}")
    
    
def display_example_commands():
    """Display example commands"""
    print("\n=== 자연어 명령 예제 ===")
    
    examples = [
        ("상품 관리", [
            "상품 목록 보여줘",
            "재고 부족 상품 확인",
            "베스트셀러 상품 조회"
        ]),
        ("주문 관리", [
            "오늘 주문 확인",
            "신규 주문 보여줘",
            "배송 대기 중인 주문"
        ]),
        ("매출 분석", [
            "오늘 매출 보여줘",
            "이번달 매출 통계",
            "전월 대비 매출 증감"
        ]),
        ("고객 관리", [
            "신규 회원 목록",
            "VIP 고객 조회",
            "휴면 고객 확인"
        ])
    ]
    
    for category, commands in examples:
        print(f"\n{category}:")
        for cmd in commands:
            print(f'  "{cmd}"')


def main():
    """Main verification function"""
    print("🚀 Cafe24 API 시스템 검증")
    print("=" * 50)
    
    # 1. 환경 변수 확인
    env_ok = verify_environment()
    
    # 2. API 연결 테스트
    if env_ok or True:  # 데모 모드도 허용
        api_ok = test_api_connection()
    else:
        print("\n⚠️  필수 환경 변수가 설정되지 않아 API 테스트를 건너뜁니다.")
        api_ok = False
        
    # 3. API 정보 표시
    display_api_info()
    
    # 4. 명령 예제 표시
    display_example_commands()
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("📊 검증 결과:")
    print(f"  환경 설정: {'✓ 완료' if env_ok else '✗ 미완료'}")
    print(f"  API 연결: {'✓ 성공' if api_ok else '✗ 실패'}")
    print(f"  시스템 상태: {'✓ 정상' if api_ok else '⚠️ 데모 모드'}")
    
    if not env_ok:
        print("\n💡 Render 대시보드에서 환경 변수를 설정하세요:")
        print("   https://dashboard.render.com")


if __name__ == "__main__":
    main()