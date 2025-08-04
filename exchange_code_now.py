#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
받은 코드로 즉시 토큰 교환
"""
import json
import requests
import base64
from datetime import datetime, timedelta

# 받은 인증 코드
AUTH_CODE = "YswhX471LN3iHeCfe6tmTP"

def exchange_token():
    """토큰 교환"""
    print("=" * 60)
    print("토큰 교환 시작")
    print("=" * 60)
    print(f"인증 코드: {AUTH_CODE}")
    
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
        'code': AUTH_CODE,
        'redirect_uri': 'https://cafe24-automation.onrender.com/callback'
    }
    
    print("\n토큰 교환 요청 중...")
    
    try:
        response = requests.post(token_url, headers=headers, data=data)
        
        print(f"응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            
            print("\n[성공] 토큰 발행 완료!")
            print(f"Access Token: {token_data['access_token'][:30]}...")
            print(f"Refresh Token: {token_data.get('refresh_token', 'N/A')[:30]}...")
            print(f"만료 시간: {token_data.get('expires_in', 7200)}초")
            
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
            
            print("\n[완료] oauth_token.json 파일 업데이트됨")
            
            # API 테스트
            test_api(full_config)
            
            # Render 환경변수 생성
            create_render_env(full_config)
            
            return True
            
        else:
            print(f"\n[실패] 토큰 교환 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n[오류] {e}")
        return False

def test_api(config):
    """API 테스트"""
    print(f"\n" + "=" * 60)
    print("API 연결 테스트")
    print("=" * 60)
    
    headers = {
        'Authorization': f'Bearer {config["access_token"]}',
        'Content-Type': 'application/json',
        'X-Cafe24-Api-Version': '2025-06-01'
    }
    
    test_url = f"https://{config['mall_id']}.cafe24api.com/api/v2/admin/products?limit=5"
    
    try:
        response = requests.get(test_url, headers=headers)
        
        print(f"API 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])
            print(f"\n[성공] API 연결 성공!")
            print(f"상품 개수: {len(products)}개")
            
            for i, product in enumerate(products[:3], 1):
                name = product.get('product_name', '알 수 없음')
                price = product.get('price', '0')
                print(f"  {i}. {name} - {price}원")
            
            return True
        else:
            print(f"\n[실패] API 테스트 실패: {response.status_code}")
            print(f"응답: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"\n[오류] API 테스트 오류: {e}")
        return False

def create_render_env(config):
    """Render 환경변수 파일 생성"""
    print(f"\n" + "=" * 60)
    print("Render 배포 파일 생성")
    print("=" * 60)
    
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

    with open('FINAL_RENDER_ENV.txt', 'w') as f:
        f.write(env_content)
    
    print(f"[완료] FINAL_RENDER_ENV.txt 파일 생성됨")
    
    print(f"\n" + "=" * 80)
    print("🎉 성공! 다음 단계를 진행하세요:")
    print("=" * 80)
    print("1. FINAL_RENDER_ENV.txt 파일 내용을 모두 복사")
    print("2. https://dashboard.render.com/ 로 이동")
    print("3. 서비스 → Environment 탭")
    print("4. 기존 환경변수 모두 삭제")
    print("5. 새 환경변수 붙여넣기 → Save Changes")
    print("6. Manual Deploy → Deploy latest commit")
    print("7. 5분 후 https://cafe24-automation.onrender.com/api/status 테스트")
    print("=" * 80)

if __name__ == "__main__":
    if exchange_token():
        print(f"\n✅ 모든 작업 완료! Render에 배포하세요!")
    else:
        print(f"\n❌ 토큰 교환 실패")