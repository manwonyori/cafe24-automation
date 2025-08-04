#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cafe24 OAuth 토큰 획득 도우미
브라우저를 통한 OAuth 인증 자동화
"""

import webbrowser
import time
import requests
from urllib.parse import urlencode, parse_qs, urlparse
import base64
import json


def get_cafe24_token():
    """Cafe24 OAuth 토큰 획득"""
    
    # 기본 정보 (기존 파일에서 읽기)
    config_path = r"C:\Users\8899y\Documents\카페24_프로젝트\01_ACTIVE_PROJECT\config\oauth_token.json"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            mall_id = config['mall_id']
            client_id = config['client_id']
            client_secret = config['client_secret']
    except:
        print("기존 설정을 찾을 수 없습니다. 수동으로 입력하세요:")
        mall_id = input("Mall ID (예: manwonyori): ").strip()
        client_id = input("Client ID: ").strip()
        client_secret = input("Client Secret: ").strip()
    
    print(f"\n설정 정보:")
    print(f"Mall ID: {mall_id}")
    print(f"Client ID: {client_id[:10]}...")
    print(f"Client Secret: {client_secret[:10]}...")
    
    # OAuth URL 생성
    redirect_uri = "https://cafe24-automation.onrender.com/callback"
    scope = "mall.read_product,mall.write_product,mall.read_order,mall.write_order,mall.read_customer"
    
    # 1. 인증 URL 생성
    auth_params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'state': 'test123'
    }
    
    auth_url = f"https://{mall_id}.cafe24api.com/api/v2/oauth/authorize?" + urlencode(auth_params)
    
    print(f"\n1. 브라우저에서 다음 URL을 열어주세요:")
    print("-" * 80)
    print(auth_url)
    print("-" * 80)
    
    # 브라우저 자동 열기
    try:
        webbrowser.open(auth_url)
        print("\n브라우저가 자동으로 열렸습니다.")
    except:
        print("\n브라우저를 수동으로 열고 위 URL을 복사해서 접속하세요.")
    
    print("\n2. Cafe24 로그인 후 권한 승인")
    print("3. 리다이렉트된 URL을 복사해서 여기에 붙여넣으세요")
    print("   (https://cafe24-automation.onrender.com/callback?code=... 형태)")
    
    # 사용자로부터 리다이렉트 URL 받기
    redirect_url = input("\n리다이렉트된 전체 URL: ").strip()
    
    # code 파라미터 추출
    parsed = urlparse(redirect_url)
    params = parse_qs(parsed.query)
    
    if 'code' not in params:
        print("오류: code 파라미터를 찾을 수 없습니다.")
        return None
        
    auth_code = params['code'][0]
    print(f"\n인증 코드: {auth_code[:20]}...")
    
    # 2. Access Token 요청
    token_url = f"https://{mall_id}.cafe24api.com/api/v2/oauth/token"
    
    token_data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': redirect_uri
    }
    
    # Basic Auth 헤더 생성
    auth_string = f"{client_id}:{client_secret}"
    auth_header = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    print("\n토큰 요청 중...")
    
    try:
        response = requests.post(token_url, data=token_data, headers=headers)
        
        if response.status_code == 200:
            token_info = response.json()
            
            print("\n✅ 토큰 발급 성공!")
            print(f"Access Token: {token_info['access_token'][:30]}...")
            print(f"Refresh Token: {token_info['refresh_token'][:30]}...")
            print(f"만료 시간: {token_info.get('expires_in', 7200)}초")
            
            # 설정 파일 업데이트
            if config_path:
                config['access_token'] = token_info['access_token']
                config['refresh_token'] = token_info['refresh_token']
                config['expires_at'] = time.strftime('%Y-%m-%dT%H:%M:%S.000')
                
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                    
                print(f"\n설정 파일 업데이트: {config_path}")
            
            # Render 환경변수용 파일 생성
            env_content = f"""CAFE24_MALL_ID={mall_id}
CAFE24_CLIENT_ID={client_id}
CAFE24_CLIENT_SECRET={client_secret}
CAFE24_REDIRECT_URI={redirect_uri}
CAFE24_ACCESS_TOKEN={token_info['access_token']}
CAFE24_REFRESH_TOKEN={token_info['refresh_token']}"""
            
            with open("new_oauth_tokens.txt", "w") as f:
                f.write(env_content)
                
            print("\n📄 new_oauth_tokens.txt 파일 생성됨")
            print("\n다음 단계:")
            print("1. new_oauth_tokens.txt 내용 복사")
            print("2. https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg/env")
            print("3. 환경변수 업데이트 후 Deploy")
            
            return token_info
            
        else:
            print(f"\n❌ 토큰 요청 실패: {response.status_code}")
            print(f"응답: {response.text}")
            
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        
    return None


def simple_method():
    """더 간단한 방법 안내"""
    print("\n" + "=" * 80)
    print("🔑 더 간단한 토큰 발급 방법")
    print("=" * 80)
    
    print("\n방법 1: Cafe24 관리자에서 직접 발급")
    print("1. Cafe24 관리자 로그인")
    print("2. 상단 메뉴 > 앱스토어 > 개발자센터")
    print("3. 내 앱 선택")
    print("4. '테스트' 또는 'Playground' 메뉴")
    print("5. 'Access Token 발급' 버튼 클릭")
    print("6. 토큰 복사")
    
    print("\n방법 2: 개발자센터 Quick Start")
    print("1. https://developers.cafe24.com")
    print("2. Quick Start 가이드 따라하기")
    print("3. 테스트 토큰 즉시 발급")
    
    print("\n토큰을 받으면:")
    print("1. 위 스크립트 재실행")
    print("2. 또는 수동으로 Render 환경변수 업데이트")


if __name__ == "__main__":
    print("Cafe24 OAuth 토큰 획득 도우미")
    print("=" * 80)
    
    choice = input("\n1. OAuth 플로우로 토큰 발급\n2. 간단한 방법 안내\n선택 (1 또는 2): ")
    
    if choice == "1":
        get_cafe24_token()
    else:
        simple_method()