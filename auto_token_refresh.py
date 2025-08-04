#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cafe24 자동 토큰 갱신 및 Render 동기화
매번 API 호출 시 토큰을 자동으로 갱신
"""

import os
import sys
import json
import requests
import subprocess
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from oauth_manager import Cafe24OAuthManager


class AutoTokenRefresher:
    def __init__(self):
        self.config = self.load_config()
        self.oauth_manager = None
        if self.config:
            self.oauth_manager = Cafe24OAuthManager(self.config)
            
    def load_config(self):
        """설정 파일 로드"""
        config_paths = [
            r"C:\Users\8899y\Documents\카페24_프로젝트\01_ACTIVE_PROJECT\config\oauth_token.json",
            "config/oauth_token.json"
        ]
        
        for path in config_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        return None
        
    def check_and_refresh_token(self):
        """토큰 상태 확인 및 자동 갱신"""
        print("=" * 60)
        print("Cafe24 자동 토큰 갱신 시스템")
        print("=" * 60)
        
        if not self.oauth_manager:
            print("[ERROR] OAuth manager not initialized")
            return False
            
        # 1. 현재 토큰 상태 확인
        print("\n1. 현재 토큰 상태 확인...")
        
        if self.oauth_manager.is_authenticated():
            token = self.oauth_manager.get_valid_token()
            if token:
                print("   [OK] Token is valid")
                return True
        
        print("   [INFO] Token needs refresh")
        
        # 2. 토큰 갱신 시도
        print("\n2. 토큰 자동 갱신 시도...")
        
        new_token = self.oauth_manager.refresh_access_token()
        
        if new_token:
            print(f"   [SUCCESS] New token obtained!")
            print(f"   Access Token: {new_token[:20]}...")
            
            # 3. 설정 파일 업데이트
            self.update_config_file(new_token)
            
            # 4. Render 환경변수 업데이트
            self.update_render_env(new_token)
            
            # 5. GitHub Actions 트리거 (자동 동기화)
            self.trigger_github_sync()
            
            return True
        else:
            print("   [FAILED] Could not refresh token")
            print("\n   가능한 원인:")
            print("   1. Refresh token도 만료됨 (2주 경과)")
            print("   2. 네트워크 문제")
            print("   3. Cafe24 API 서버 문제")
            
            return False
            
    def update_config_file(self, new_token):
        """설정 파일에 새 토큰 저장"""
        print("\n3. 설정 파일 업데이트...")
        
        config_path = r"C:\Users\8899y\Documents\카페24_프로젝트\01_ACTIVE_PROJECT\config\oauth_token.json"
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # 새 토큰 정보 업데이트
            config['access_token'] = new_token
            config['expires_at'] = (datetime.now() + timedelta(hours=2)).isoformat() + '.000'
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
            print("   [OK] Config file updated")
            
    def update_render_env(self, new_token):
        """Render 환경변수 업데이트용 파일 생성"""
        print("\n4. Render 환경변수 준비...")
        
        env_content = f"""CAFE24_MALL_ID={self.config['mall_id']}
CAFE24_CLIENT_ID={self.config['client_id']}
CAFE24_CLIENT_SECRET={self.config['client_secret']}
CAFE24_REDIRECT_URI=https://cafe24-automation.onrender.com/callback
CAFE24_ACCESS_TOKEN={new_token}
CAFE24_REFRESH_TOKEN={self.config['refresh_token']}"""
        
        with open("render_env_auto_updated.txt", "w") as f:
            f.write(env_content)
            
        print("   [OK] render_env_auto_updated.txt created")
        
    def trigger_github_sync(self):
        """GitHub Actions를 통한 자동 동기화"""
        print("\n5. GitHub Actions 자동 동기화...")
        
        try:
            # GitHub Secrets 업데이트
            result = subprocess.run(
                ['gh', 'secret', 'set', 'CAFE24_ACCESS_TOKEN'],
                input=self.oauth_manager.token_data.get('access_token', ''),
                text=True,
                capture_output=True
            )
            
            if result.returncode == 0:
                print("   [OK] GitHub Secret updated")
                
                # Workflow 트리거
                result = subprocess.run(
                    ['gh', 'workflow', 'run', 'auto-deploy.yml'],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    print("   [OK] Deployment triggered")
                    print("   모니터링: https://github.com/manwonyori/cafe24/actions")
                else:
                    print("   [WARN] Could not trigger workflow")
            else:
                print("   [WARN] Could not update GitHub Secret")
                
        except Exception as e:
            print(f"   [ERROR] {e}")
            
        print("\n   수동 업데이트 방법:")
        print("   1. render_env_auto_updated.txt 내용 복사")
        print("   2. https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg/env")
        print("   3. 환경변수 업데이트 후 Deploy")
        
    def setup_auto_refresh_in_app(self):
        """앱에 자동 갱신 로직 추가"""
        print("\n6. 앱 자동 갱신 설정...")
        
        # api_client.py 수정 제안
        print("\n   api_client.py에 추가할 코드:")
        print("   " + "-" * 40)
        print("""
    def _request(self, method: str, endpoint: str, **kwargs):
        # 토큰 자동 갱신 체크
        if not self.oauth_manager.is_authenticated():
            new_token = self.oauth_manager.refresh_access_token()
            if new_token:
                self.headers['Authorization'] = f'Bearer {new_token}'
                # Render 환경변수도 업데이트 트리거
                
        response = self.session.request(method, url, **kwargs)
        
        # 401 또는 403 응답 시 토큰 갱신 재시도
        if response.status_code in [401, 403]:
            new_token = self.oauth_manager.refresh_access_token()
            if new_token:
                self.headers['Authorization'] = f'Bearer {new_token}'
                response = self.session.request(method, url, **kwargs)
        """)
        print("   " + "-" * 40)
        

def main():
    print("Cafe24 자동 토큰 갱신 시작...\n")
    
    refresher = AutoTokenRefresher()
    
    # 토큰 갱신 실행
    success = refresher.check_and_refresh_token()
    
    if success:
        print("\n✅ 토큰 갱신 성공!")
        print("\n다음 단계:")
        print("1. GitHub Actions가 자동으로 Render에 배포")
        print("2. 또는 render_env_auto_updated.txt 내용을 수동으로 적용")
        
        # 자동 갱신 설정 제안
        refresher.setup_auto_refresh_in_app()
    else:
        print("\n❌ 토큰 갱신 실패")
        print("\n해결 방법:")
        print("1. Cafe24 개발자센터에서 수동으로 토큰 재발급")
        print("2. https://developers.cafe24.com")
        
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()