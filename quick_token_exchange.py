#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
카페24 토큰 빠른 교환 스크립트
새 인증 코드로 액세스 토큰을 발급받는 스크립트
"""
import requests
import json
from datetime import datetime, timedelta

def exchange_auth_code():
    """인증 코드를 액세스 토큰으로 교환"""
    print("=" * 50)
    print("카페24 토큰 발급")
    print("=" * 50)
    
    # 기존 설정 읽기
    client_id = "9bPpABwHB5mtkCEAfIeuNK"
    client_secret = "qtnWtUk2OZzua1SRa7gN3A"
    redirect_uri = "https://cafe24-automation.onrender.com/auth/callback"
    mall_id = "manwonyori"
    
    print("현재 설정:")
    print(f"  Client ID: {client_id}")
    print(f"  Mall ID: {mall_id}")
    print(f"  Redirect URI: {redirect_uri}")
    print()
    
    # 인증 URL 생성
    auth_url = f"https://{mall_id}.cafe24api.com/api/v2/oauth/authorize"
    auth_params = {
        'response_type': 'code',
        'client_id': client_id,
        'state': 'cafe24_auth',
        'redirect_uri': redirect_uri,
        'scope': 'mall.read_product,mall.write_product,mall.read_order,mall.write_order,mall.read_customer'
    }
    
    full_auth_url = auth_url + "?" + "&".join([f"{k}={v}" for k, v in auth_params.items()])
    
    print("1단계: 다음 URL에서 인증 코드를 받으세요:")
    print("-" * 50)
    print(full_auth_url)
    print("-" * 50)
    print()
    
    # 사용자로부터 인증 코드 입력받기
    print("2단계: 받은 인증 코드를 입력하세요:")
    auth_code = input("인증 코드: ").strip()
    
    if not auth_code:
        print("[오류] 인증 코드를 입력해주세요.")
        return False
    
    print()
    print("3단계: 토큰 발급 중...")
    
    # 토큰 교환 요청
    token_url = f"https://{mall_id}.cafe24api.com/api/v2/oauth/token"
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'code': auth_code
    }
    
    try:
        response = requests.post(token_url, data=token_data, timeout=15)
        
        if response.status_code == 200:
            token_response = response.json()
            
            # 토큰 데이터 구성
            now = datetime.now()
            expires_in = token_response.get('expires_in', 7200)
            
            token_data = {
                'access_token': token_response['access_token'],
                'refresh_token': token_response['refresh_token'],
                'expires_at': (now + timedelta(seconds=expires_in)).isoformat(),
                'refresh_token_expires_at': (now + timedelta(days=14)).isoformat(),
                'client_id': client_id,
                'client_secret': client_secret,
                'mall_id': mall_id,
                'user_id': mall_id,
                'scopes': [
                    'mall.read_product',
                    'mall.write_product', 
                    'mall.read_order',
                    'mall.write_order',
                    'mall.read_customer'
                ],
                'issued_at': now.isoformat(),
                'shop_no': '1'
            }
            
            # 토큰 파일 저장
            with open('oauth_token.json', 'w', encoding='utf-8') as f:
                json.dump(token_data, f, ensure_ascii=False, indent=2)
            
            print("[성공] 토큰이 발급되었습니다!")
            print(f"  액세스 토큰: ***{token_data['access_token'][-10:]}")
            print(f"  만료 시간: {token_data['expires_at']}")
            print(f"  파일 위치: oauth_token.json")
            print()
            
            # 즉시 테스트
            print("4단계: 토큰 테스트 중...")
            test_success = test_new_token(token_data['access_token'], mall_id)
            
            if test_success:
                print("[완료] 토큰이 정상적으로 작동합니다!")
            else:
                print("[경고] 토큰 테스트에 실패했습니다. 다시 시도해보세요.")
            
            return test_success
            
        else:
            print(f"[실패] 토큰 발급 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"[오류] 토큰 발급 중 오류: {str(e)}")
        return False

def test_new_token(access_token, mall_id):
    """새 토큰 테스트"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Cafe24-Api-Version': '2025-06-01'
    }
    
    test_url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products/count"
    
    try:
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print(f"  테스트 결과: 상품 수량 {count}개 조회 성공")
            return True
        else:
            print(f"  테스트 실패: {response.status_code} - {response.text[:100]}")
            return False
            
    except Exception as e:
        print(f"  테스트 오류: {str(e)}")
        return False

def main():
    """메인 함수"""
    success = exchange_auth_code()
    
    if success:
        print()
        print("=" * 50)
        print("토큰 발급이 완료되었습니다!")
        print("이제 comprehensive_api_test.py를 실행하여")
        print("전체 시스템을 다시 테스트해보세요.")
        print("=" * 50)
    else:
        print()
        print("=" * 50)
        print("토큰 발급에 실패했습니다.")
        print("인증 코드를 다시 확인하고 재시도하세요.")
        print("=" * 50)

if __name__ == '__main__':
    main()