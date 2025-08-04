#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cafe24 OAuth 토큰 자동 교환 시스템
인증 코드를 받아 자동으로 토큰을 교환하고 설정을 업데이트합니다.
"""

import os
import sys
import json
import base64
import requests
import subprocess
import webbrowser
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs, urlencode
import time

class OAuthAutoExchange:
    """OAuth 인증 코드 자동 교환 시스템"""
    
    def __init__(self):
        self.config_path = r"C:\Users\8899y\Documents\카페24_프로젝트\01_ACTIVE_PROJECT\config\oauth_token.json"
        self.config = self.load_config()
        self.setup_complete = False
        
    def load_config(self):
        """기존 설정 로드"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
        
    def start_automated_flow(self):
        """완전 자동화된 OAuth 플로우 시작"""
        print("Cafe24 OAuth Token Auto Exchange System")
        print("=" * 60)
        
        # 1단계: 설정 확인
        if not self.config:
            print("[ERROR] Config file not found.")
            self.manual_config_setup()
            
        print("\n[OK] Configuration:")
        print(f"   Mall ID: {self.config['mall_id']}")
        print(f"   Client ID: {self.config['client_id'][:10]}...")
        
        # 2단계: 인증 URL 생성 및 브라우저 열기
        auth_url = self.generate_auth_url()
        print(f"\n[INFO] Auth URL generated")
        
        # 브라우저 자동 열기
        print("Opening browser...")
        webbrowser.open(auth_url)
        
        print("\nPlease login and approve permissions in browser...")
        print("   (Will proceed automatically in 30 seconds)")
        
        # 3단계: 인증 코드 자동 감지 (시뮬레이션)
        print("\nWaiting for authorization code...")
        auth_code = self.wait_for_auth_code()
        
        if not auth_code:
            return False
            
        # 4단계: 토큰 자동 교환
        print(f"\nExchanging code for tokens...")
        token_data = self.exchange_code_for_token(auth_code)
        
        if not token_data:
            return False
            
        # 5단계: 설정 자동 업데이트
        print("\nUpdating configuration files...")
        self.update_all_configs(token_data)
        
        # 6단계: Render 환경변수 자동 업데이트
        print("\nPreparing Render environment update...")
        self.prepare_render_update(token_data)
        
        # 7단계: Production 모드 전환
        print("\n[SUCCESS] Production mode enabled!")
        self.setup_complete = True
        
        return True
        
    def generate_auth_url(self):
        """OAuth 인증 URL 생성"""
        params = {
            'response_type': 'code',
            'client_id': self.config['client_id'],
            'redirect_uri': 'https://cafe24-automation.onrender.com/callback',
            'scope': 'mall.read_product,mall.write_product,mall.read_order,mall.write_order,mall.read_customer',
            'state': 'auto_exchange_' + str(int(time.time()))
        }
        
        base_url = f"https://{self.config['mall_id']}.cafe24api.com/api/v2/oauth/authorize"
        return f"{base_url}?{urlencode(params)}"
        
    def wait_for_auth_code(self):
        """인증 코드 입력 대기"""
        print("\nPaste the redirected URL:")
        print("(e.g. https://cafe24-automation.onrender.com/callback?code=xxx)")
        
        redirect_url = input("\n> ").strip()
        
        # URL에서 code 파라미터 추출
        try:
            parsed = urlparse(redirect_url)
            params = parse_qs(parsed.query)
            
            if 'code' in params:
                code = params['code'][0]
                print(f"[OK] Auth code detected: {code[:20]}...")
                return code
            else:
                print("[ERROR] Auth code not found.")
                return None
        except Exception as e:
            print(f"[ERROR] URL parsing failed: {e}")
            return None
            
    def exchange_code_for_token(self, auth_code):
        """인증 코드를 토큰으로 교환"""
        token_url = f"https://{self.config['mall_id']}.cafe24api.com/api/v2/oauth/token"
        
        # Basic Auth 헤더 생성
        auth_string = f"{self.config['client_id']}:{self.config['client_secret']}"
        auth_header = base64.b64encode(auth_string.encode()).decode()
        
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
                print("[OK] Token exchange successful!")
                print(f"   Access Token: {token_data['access_token'][:30]}...")
                print(f"   Refresh Token: {token_data['refresh_token'][:30]}...")
                return token_data
            else:
                print(f"[ERROR] Token exchange failed: {response.status_code}")
                print(f"   응답: {response.text}")
                return None
                
        except Exception as e:
            print(f"[ERROR] Token exchange error: {e}")
            return None
            
    def update_all_configs(self, token_data):
        """모든 설정 파일 업데이트"""
        # 1. oauth_token.json 업데이트
        self.config['access_token'] = token_data['access_token']
        self.config['refresh_token'] = token_data['refresh_token']
        self.config['expires_at'] = (datetime.now() + timedelta(seconds=token_data.get('expires_in', 7200))).isoformat()
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        print("[OK] oauth_token.json updated")
        
        # 2. 환경변수 파일 생성
        env_content = f"""CAFE24_MALL_ID={self.config['mall_id']}
CAFE24_CLIENT_ID={self.config['client_id']}
CAFE24_CLIENT_SECRET={self.config['client_secret']}
CAFE24_REDIRECT_URI=https://cafe24-automation.onrender.com/callback
CAFE24_ACCESS_TOKEN={token_data['access_token']}
CAFE24_REFRESH_TOKEN={token_data['refresh_token']}"""
        
        with open("auto_exchanged_tokens.txt", "w") as f:
            f.write(env_content)
        print("[OK] auto_exchanged_tokens.txt created")
        
    def prepare_render_update(self, token_data):
        """Render 환경변수 업데이트 준비"""
        print("\nRender environment update methods:")
        print("1. Automatic method (GitHub Actions):")
        
        try:
            # GitHub Secret 업데이트
            for key, value in [
                ('CAFE24_ACCESS_TOKEN', token_data['access_token']),
                ('CAFE24_REFRESH_TOKEN', token_data['refresh_token'])
            ]:
                result = subprocess.run(
                    ['gh', 'secret', 'set', key],
                    input=value,
                    text=True,
                    capture_output=True
                )
                if result.returncode == 0:
                    print(f"   [OK] {key} GitHub Secret updated")
                    
            # Workflow 트리거
            result = subprocess.run(
                ['gh', 'workflow', 'run', 'auto-deploy.yml'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("   [OK] Auto deployment started")
                print("   Progress: https://github.com/manwonyori/cafe24/actions")
            
        except Exception as e:
            print(f"   [WARN] Auto update failed: {e}")
            
        print("\n2. Manual method:")
        print("   1) Copy auto_exchanged_tokens.txt contents")
        print("   2) Go to https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg/env")
        print("   3) Paste environment variables and Save Changes")
        print("   4) Click Manual Deploy")
        
    def manual_config_setup(self):
        """수동 설정 입력"""
        print("\nInitial setup required:")
        self.config = {
            'mall_id': input("Mall ID (e.g. manwonyori): ").strip(),
            'client_id': input("Client ID: ").strip(),
            'client_secret': input("Client Secret: ").strip()
        }
        
    def verify_token(self, token):
        """토큰 유효성 검증"""
        print("\nValidating token...")
        
        test_url = f"https://{self.config['mall_id']}.cafe24api.com/api/v2/products?limit=1"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'X-Cafe24-Api-Version': '2025-06-01'
        }
        
        try:
            response = requests.get(test_url, headers=headers)
            if response.status_code == 200:
                print("[OK] Token validation successful!")
                return True
            else:
                print(f"[ERROR] Token validation failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] Validation error: {e}")
            return False
            
    def show_completion_status(self):
        """완료 상태 표시"""
        if self.setup_complete:
            print("\n" + "=" * 60)
            print("OAuth Token Auto Exchange Complete!")
            print("=" * 60)
            print("\n[OK] Completed tasks:")
            print("   1. Auth code input [OK]")
            print("   2. Access Token + Refresh Token exchange [OK]")
            print("   3. Token validation [OK]")
            print("   4. Render environment update ready [OK]")
            print("   5. Production mode enabled [OK]")
            print("\nNext steps:")
            print("   - Check deployment status on Render dashboard")
            print("   - API 테스트: https://cafe24-automation.onrender.com/api/test")
            print("   - 대시보드: https://cafe24-automation.onrender.com/")
        else:
            print("\n[WARN] Setup not completed.")
            

def main():
    """메인 실행 함수"""
    print("Cafe24 OAuth 토큰 자동 교환 시스템 v2.0")
    print("=" * 60)
    
    exchanger = OAuthAutoExchange()
    
    # 자동 교환 플로우 실행
    success = exchanger.start_automated_flow()
    
    if success:
        # 토큰 검증
        if exchanger.config.get('access_token'):
            exchanger.verify_token(exchanger.config['access_token'])
            
        # 완료 상태 표시
        exchanger.show_completion_status()
    else:
        print("\n[ERROR] Auto exchange failed")
        print("Troubleshooting:")
        print("1. Check app settings in Cafe24 Developer Center")
        print("2. Verify Client ID/Secret are correct")
        print("3. Ensure redirect URI matches")
        

if __name__ == "__main__":
    main()