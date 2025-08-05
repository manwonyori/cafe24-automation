#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
"""
API 가격 수정이 실제로 작동하도록 수정
"""
import requests
import json

# 문제 분석
print("=== Cafe24 API 가격 수정 문제 해결 ===\n")

print("현재 문제:")
print("1. API가 200 OK를 반환하지만 실제 변경 안됨")
print("2. 옵션 상품(has_option: True)이라서 복잡함")
print("3. 권한 문제일 가능성\n")

print("해결 방법:")
print("\n[방법 1] 다른 API 엔드포인트 사용")
print("- PUT /products/{id}/options/{option_id}/values")
print("- 각 옵션별로 가격 수정")

print("\n[방법 2] 상품 전체 업데이트")
print("- 모든 필드를 포함한 전체 업데이트")
print("- price, retail_price, supply_price 모두 수정")

print("\n[방법 3] Cafe24 개발자센터 확인")
print("- OAuth 앱 권한 확인")
print("- 'mall.write_product' 권한 필요")
print("- https://developers.cafe24.com")

# 실제 테스트
with open('oauth_token.json', 'r', encoding='utf-8') as f:
    token_data = json.load(f)

headers = {
    'Authorization': f'Bearer {token_data["access_token"]}',
    'Content-Type': 'application/json',
    'X-Cafe24-Api-Version': '2025-06-01'
}

# 권한 확인
print("\n\n=== 현재 OAuth 권한 확인 ===")
url = f"https://{token_data['mall_id']}.cafe24api.com/api/v2/oauth/me"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    scopes = data.get('scopes', [])
    print(f"현재 권한: {scopes}")
    
    if 'mall.write_product' in scopes:
        print("✅ 상품 수정 권한 있음")
    else:
        print("❌ 상품 수정 권한 없음!")
        print("\n해결:")
        print("1. Cafe24 개발자센터 접속")
        print("2. 앱 설정 > 권한 관리")
        print("3. 'mall.write_product' 권한 추가")
        print("4. 토큰 재발급")

# 다른 방법 시도
print("\n\n=== 대안: 상품 일괄 수정 API ===")
print("POST /api/v2/admin/products/batch")
print("여러 상품을 한번에 수정하는 API")
print("하지만 Cafe24 API 문서를 확인해야 함")

print("\n\n=== 결론 ===")
print("1. 먼저 OAuth 권한 확인")
print("2. 권한이 있다면 다른 API 방식 시도")
print("3. 그래도 안되면 Cafe24 고객센터 문의")
print("4. 또는 Selenium 등으로 관리자 페이지 자동화")