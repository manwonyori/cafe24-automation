#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 토큰 교환 스크립트
"""
import json
import requests
import base64
from datetime import datetime, timedelta

def get_auth_url():
    """인증 URL 출력"""
    print("=" * 80)
    print("CAFE24 TOKEN 발행")
    print("=" * 80)
    
    auth_url = "https://manwonyori.cafe24api.com/api/v2/oauth/authorize?response_type=code&client_id=9bPpABwHB5mtkCEAfIeuNK&redirect_uri=https://cafe24-automation.onrender.com/callback&scope=mall.read_product,mall.write_product,mall.read_order,mall.write_order,mall.read_customer"
    
    print(f"\n1. 이 URL을 브라우저에서 열어주세요:")
    print(f"{auth_url}")
    print(f"\n2. Cafe24에 로그인하고 앱을 승인하세요")
    print(f"3. 리다이렉트된 URL에서 code= 뒤의 코드를 복사하세요")
    print(f"   예: https://cafe24-automation.onrender.com/callback?code=ABC123")
    print(f"   여기서 ABC123 부분을 복사")
    
    return input(f"\n인증 코드를 입력하세요: ").strip()

def exchange_token(auth_code):
    """토큰 교환"""
    print(f"\n받은 코드: {auth_code}")
    print("토큰 교환 중...")
    
    config = {
        'mall_id': 'manwonyori',
        'client_id': '9bPpABwHB5mtkCEAfIeuNK',
        'client_secret': 'qtnWtUk2OZzua1SRa7gN3A'
    }
    
    token_url = f"https://{config['mall_id']}.cafe24api.com/api/v2/oauth/token"
    
    auth_header = base64.b64encode(f"{config['client_id']}:{config['client_secret']}".encode()).decode()
    
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': 'https://cafe24-automation.onrender.com/callback'
    }
    
    try:
        response = requests.post(token_url, headers=headers, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            
            print("[성공] 토큰 발행 완료!")
            print(f"Access Token: {token_data['access_token'][:30]}...")
            
            # 완전한 설정 생성
            full_config = {
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token', ''),
                'expires_at': (datetime.now() + timedelta(seconds=token_data.get('expires_in', 7200))).isoformat() + '.000',
                'refresh_token_expires_at': (datetime.now() + timedelta(seconds=token_data.get('refresh_token_expires_in', 1209600))).isoformat() + '.000',
                'client_id': config['client_id'],
                'client_secret': config['client_secret'],
                'mall_id': config['mall_id'],
                'user_id': config['mall_id'],
                'scopes': ['mall.read_product', 'mall.write_product', 'mall.read_order', 'mall.write_order', 'mall.read_customer'],
                'issued_at': datetime.now().isoformat() + '.000',
                'shop_no': '1'
            }
            
            # 저장
            with open('oauth_token.json', 'w', encoding='utf-8') as f:
                json.dump(full_config, f, indent=2, ensure_ascii=False)
            
            # API 테스트
            test_api(full_config)
            
            # Render 환경변수 생성
            create_render_env(full_config)
            
            return True
            
        else:
            print(f"[실패] 토큰 교환 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"[오류] {e}")
        return False

def test_api(config):
    """API 테스트"""
    print(f"\nAPI 연결 테스트 중...")
    
    headers = {
        'Authorization': f'Bearer {config["access_token"]}',
        'Content-Type': 'application/json',
        'X-Cafe24-Api-Version': '2025-06-01'
    }
    
    test_url = f"https://{config['mall_id']}.cafe24api.com/api/v2/admin/products?limit=3"
    
    try:
        response = requests.get(test_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])
            print(f"[성공] API 연결 성공! 상품 {len(products)}개 발견")
            return True
        else:
            print(f"[실패] API 테스트 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[오류] API 테스트 오류: {e}")
        return False

def create_render_env(config):
    """Render 환경변수 파일 생성"""
    env_content = f"""CAFE24_MALL_ID={config['mall_id']}
CAFE24_CLIENT_ID={config['client_id']}
CAFE24_CLIENT_SECRET={config['client_secret']}
CAFE24_REDIRECT_URI=https://cafe24-automation.onrender.com/callback
CAFE24_ACCESS_TOKEN={config['access_token']}
CAFE24_REFRESH_TOKEN={config['refresh_token']}
CAFE24_API_VERSION=2025-06-01
ENABLE_AUTO_REFRESH=true
ENABLE_DASHBOARD=true
ENABLE_API_ENDPOINTS=true
PRODUCTION_MODE=true
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
PORT=5000"""

    with open('NEW_RENDER_ENV.txt', 'w') as f:
        f.write(env_content)
    
    print(f"\n[완료] NEW_RENDER_ENV.txt 파일 생성됨")
    print(f"\n다음 단계:")
    print(f"1. NEW_RENDER_ENV.txt 파일 내용을 모두 복사")
    print(f"2. https://dashboard.render.com/ 에서 Environment 설정")
    print(f"3. 기존 변수 삭제 후 새 변수 붙여넣기")
    print(f"4. Save Changes 후 Manual Deploy")

def main():
    auth_code = get_auth_url()
    if auth_code:
        if exchange_token(auth_code):
            print(f"\n[완료] 모든 작업 성공! 이제 Render에 배포하세요!")
        else:
            print(f"\n[실패] 토큰 교환 실패")
    else:
        print(f"\n[취소] 인증 코드가 입력되지 않았습니다")

if __name__ == "__main__":
    main()