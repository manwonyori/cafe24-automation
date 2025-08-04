#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cafe24 OAuth 원클릭 설정 시스템
Cafe24 앱 설정 정보를 기반으로 자동 OAuth 설정
"""

import os
import sys
import json
import base64
import requests
import webbrowser
import subprocess
from datetime import datetime, timedelta
from urllib.parse import urlencode
import time

class Cafe24OneClickSetup:
    """Cafe24 OAuth 원클릭 설정"""
    
    def __init__(self):
        self.app_info = {
            'app_url': 'https://www.manwonyori.com',
            'redirect_uri': 'https://cafe24-automation.onrender.com/callback',
            'window_type': 'new',  # 새 창 열기
            'popup_width': 900,
            'popup_height': 800
        }
        
        self.config_path = r"C:\Users\8899y\Documents\카페24_프로젝트\01_ACTIVE_PROJECT\config\oauth_token.json"
        self.load_existing_config()
        
    def load_existing_config(self):
        """기존 설정 로드"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.mall_id = config.get('mall_id', 'manwonyori')
                self.client_id = config.get('client_id')
                self.client_secret = config.get('client_secret')
                print("✅ 기존 설정 로드 완료")
        else:
            print("⚠️  설정 파일이 없습니다. 수동 입력이 필요합니다.")
            self.manual_setup()
            
    def manual_setup(self):
        """수동 설정"""
        print("\nCafe24 앱 정보를 입력하세요:")
        self.mall_id = input("Mall ID (기본: manwonyori): ").strip() or "manwonyori"
        self.client_id = input("Client ID: ").strip()
        self.client_secret = input("Client Secret: ").strip()
        
    def quick_oauth_flow(self):
        """빠른 OAuth 플로우"""
        print("\n🚀 Cafe24 OAuth 빠른 설정")
        print("=" * 60)
        
        # 1. 인증 URL 생성
        auth_url = self.build_auth_url()
        
        print(f"\n1️⃣ 인증 페이지로 이동")
        print(f"   Mall: {self.mall_id}")
        print(f"   App URL: {self.app_info['app_url']}")
        print(f"   Redirect URI: {self.app_info['redirect_uri']}")
        
        # 2. 브라우저 열기
        print("\n2️⃣ 브라우저를 여는 중...")
        webbrowser.open(auth_url)
        
        print("\n   ⏳ Cafe24에 로그인하고 권한을 승인하세요")
        print("   ✅ 승인 후 리다이렉트된 URL을 복사하세요")
        
        # 3. 인증 코드 받기
        print("\n3️⃣ 리다이렉트된 URL 입력")
        print("   (예: https://cafe24-automation.onrender.com/callback?code=xxx)")
        
        redirect_url = input("\n   URL: ").strip()
        
        # 4. 코드 추출 및 토큰 교환
        auth_code = self.extract_auth_code(redirect_url)
        if not auth_code:
            print("❌ 인증 코드를 찾을 수 없습니다.")
            return False
            
        print(f"\n4️⃣ 토큰 교환 중...")
        token_data = self.exchange_for_tokens(auth_code)
        
        if not token_data:
            print("❌ 토큰 교환 실패")
            return False
            
        # 5. 설정 저장 및 배포
        print(f"\n5️⃣ 설정 저장 및 배포 준비...")
        self.save_and_deploy(token_data)
        
        print("\n✅ OAuth 설정 완료!")
        return True
        
    def build_auth_url(self):
        """OAuth 인증 URL 생성"""
        base_url = f"https://{self.mall_id}.cafe24api.com/api/v2/oauth/authorize"
        
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.app_info['redirect_uri'],
            'scope': 'mall.read_product,mall.write_product,mall.read_order,mall.write_order,mall.read_customer',
            'state': f'cafe24_setup_{int(time.time())}'
        }
        
        return f"{base_url}?{urlencode(params)}"
        
    def extract_auth_code(self, redirect_url):
        """URL에서 인증 코드 추출"""
        try:
            if 'code=' in redirect_url:
                code = redirect_url.split('code=')[1].split('&')[0]
                print(f"   ✅ 인증 코드: {code[:20]}...")
                return code
        except:
            pass
        return None
        
    def exchange_for_tokens(self, auth_code):
        """인증 코드를 토큰으로 교환"""
        token_url = f"https://{self.mall_id}.cafe24api.com/api/v2/oauth/token"
        
        # Basic Auth
        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': self.app_info['redirect_uri']
        }
        
        try:
            response = requests.post(token_url, headers=headers, data=data)
            
            if response.status_code == 200:
                tokens = response.json()
                print(f"   ✅ Access Token: {tokens['access_token'][:30]}...")
                print(f"   ✅ Refresh Token: {tokens['refresh_token'][:30]}...")
                return tokens
            else:
                print(f"   ❌ 오류: {response.status_code}")
                print(f"   응답: {response.text}")
                
        except Exception as e:
            print(f"   ❌ 예외: {e}")
            
        return None
        
    def save_and_deploy(self, token_data):
        """설정 저장 및 배포"""
        # 1. 로컬 설정 저장
        config = {
            'mall_id': self.mall_id,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'access_token': token_data['access_token'],
            'refresh_token': token_data['refresh_token'],
            'expires_at': (datetime.now() + timedelta(seconds=token_data.get('expires_in', 7200))).isoformat(),
            'app_url': self.app_info['app_url'],
            'redirect_uri': self.app_info['redirect_uri']
        }
        
        # 디렉토리 생성
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print("   ✅ 로컬 설정 저장")
        
        # 2. Render 환경변수 파일 생성
        env_content = f"""# Cafe24 OAuth Settings
CAFE24_MALL_ID={self.mall_id}
CAFE24_CLIENT_ID={self.client_id}
CAFE24_CLIENT_SECRET={self.client_secret}
CAFE24_REDIRECT_URI={self.app_info['redirect_uri']}
CAFE24_ACCESS_TOKEN={token_data['access_token']}
CAFE24_REFRESH_TOKEN={token_data['refresh_token']}

# App Settings
CAFE24_APP_URL={self.app_info['app_url']}
"""
        
        with open("render_env_ready.txt", "w") as f:
            f.write(env_content)
        print("   ✅ render_env_ready.txt 생성")
        
        # 3. GitHub 자동 배포 시도
        self.try_auto_deploy(token_data)
        
        # 4. 수동 배포 안내
        print("\n📋 수동 배포 방법:")
        print("   1. render_env_ready.txt 내용 복사")
        print("   2. https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg/env")
        print("   3. 환경변수 업데이트 → Save Changes")
        print("   4. Manual Deploy → Deploy latest commit")
        
    def try_auto_deploy(self, token_data):
        """GitHub Actions 자동 배포 시도"""
        try:
            print("\n   🚀 GitHub 자동 배포 시도...")
            
            # GitHub Secrets 업데이트
            secrets = [
                ('CAFE24_ACCESS_TOKEN', token_data['access_token']),
                ('CAFE24_REFRESH_TOKEN', token_data['refresh_token']),
                ('CAFE24_CLIENT_ID', self.client_id),
                ('CAFE24_CLIENT_SECRET', self.client_secret)
            ]
            
            for key, value in secrets:
                subprocess.run(
                    ['gh', 'secret', 'set', key],
                    input=value,
                    text=True,
                    capture_output=True
                )
                
            # Workflow 실행
            result = subprocess.run(
                ['gh', 'workflow', 'run', 'auto-deploy.yml'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("   ✅ 자동 배포 시작!")
                print("   📊 진행상황: https://github.com/manwonyori/cafe24/actions")
                
        except Exception as e:
            print(f"   ⚠️  자동 배포 실패: {e}")
            
    def test_api_connection(self):
        """API 연결 테스트"""
        print("\n🧪 API 연결 테스트...")
        
        if not hasattr(self, 'access_token'):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                access_token = config.get('access_token')
        else:
            access_token = self.access_token
            
        test_url = f"https://{self.mall_id}.cafe24api.com/api/v2/products?limit=1"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'X-Cafe24-Api-Version': '2025-06-01'
        }
        
        try:
            response = requests.get(test_url, headers=headers)
            if response.status_code == 200:
                print("   ✅ API 연결 성공!")
                print("   🌐 대시보드: https://cafe24-automation.onrender.com/")
                return True
            else:
                print(f"   ❌ API 오류: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ 연결 실패: {e}")
            return False
            

def main():
    """메인 실행"""
    print("🎯 Cafe24 OAuth 원클릭 설정")
    print("=" * 60)
    
    setup = Cafe24OneClickSetup()
    
    # OAuth 플로우 실행
    if setup.quick_oauth_flow():
        # API 테스트
        setup.test_api_connection()
        
        print("\n" + "=" * 60)
        print("🎉 설정 완료!")
        print("=" * 60)
        print("\n다음 단계:")
        print("1. Render 대시보드에서 배포 확인")
        print("2. https://cafe24-automation.onrender.com/ 접속")
        print("3. API 테스트 및 사용 시작")
    else:
        print("\n설정 실패. 다시 시도하세요.")
        

if __name__ == "__main__":
    main()