#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cafe24 API 오류 자동 수정 스크립트
403 Forbidden 오류 해결
"""

import os
import json
import requests
import sys
from datetime import datetime, timedelta
import subprocess


class APIErrorFixer:
    def __init__(self):
        self.errors = []
        self.fixed = []
        
    def diagnose_api_errors(self):
        """API 오류 진단"""
        print("=" * 60)
        print("Cafe24 API 오류 진단 및 수정")
        print("=" * 60)
        
        # 1. 현재 상태 확인
        print("\n1. 현재 시스템 상태 확인...")
        try:
            response = requests.get("https://cafe24-automation.onrender.com/")
            data = response.json()
            print(f"   - Mode: {data.get('mode')}")
            print(f"   - Status: {data.get('status')}")
        except Exception as e:
            print(f"   [ERROR] {e}")
            
        # 2. API 테스트
        print("\n2. API 엔드포인트 테스트...")
        test_urls = [
            "https://cafe24-automation.onrender.com/api/products?limit=1",
            "https://cafe24-automation.onrender.com/api/orders?limit=1"
        ]
        
        for url in test_urls:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    print(f"   [OK] {url.split('/')[-1].split('?')[0]}")
                else:
                    data = response.json()
                    error = data.get('error', 'Unknown error')
                    print(f"   [ERROR] {url.split('/')[-1].split('?')[0]}: {error}")
                    
                    # 403 Forbidden 분석
                    if "403" in error:
                        self.errors.append({
                            "type": "auth_error",
                            "endpoint": url,
                            "message": "OAuth token expired or insufficient permissions"
                        })
            except Exception as e:
                print(f"   [ERROR] {e}")
                
    def check_token_status(self):
        """OAuth 토큰 상태 확인"""
        print("\n3. OAuth 토큰 상태 확인...")
        
        # 로컬 토큰 파일 확인
        token_paths = [
            r"C:\Users\8899y\Documents\카페24_프로젝트\01_ACTIVE_PROJECT\config\oauth_token.json",
            "config/oauth_token.json"
        ]
        
        for path in token_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    token_data = json.load(f)
                    
                # 토큰 만료 확인
                expires_at = token_data.get('expires_at')
                if expires_at:
                    expiry = datetime.fromisoformat(expires_at.replace('.000', ''))
                    now = datetime.now()
                    
                    if now > expiry:
                        print(f"   [EXPIRED] Access token expired at {expires_at}")
                        self.errors.append({
                            "type": "token_expired",
                            "expires_at": expires_at
                        })
                    else:
                        time_left = expiry - now
                        print(f"   [OK] Token valid for {time_left}")
                        
                # 권한 확인
                scopes = token_data.get('scopes', [])
                print(f"   Scopes: {', '.join(scopes)}")
                
                missing_scopes = []
                required_scopes = [
                    "mall.read_product",
                    "mall.write_product",
                    "mall.read_order",
                    "mall.write_order"
                ]
                
                for scope in required_scopes:
                    if scope not in scopes:
                        missing_scopes.append(scope)
                        
                if missing_scopes:
                    print(f"   [WARNING] Missing scopes: {', '.join(missing_scopes)}")
                    self.errors.append({
                        "type": "missing_scopes",
                        "scopes": missing_scopes
                    })
                    
                break
                
    def generate_fixes(self):
        """수정 방법 생성"""
        print("\n4. 수정 방법...")
        
        for error in self.errors:
            if error['type'] == 'auth_error' or error['type'] == 'token_expired':
                print("\n   [FIX 1] OAuth 토큰 갱신:")
                print("   - Cafe24 개발자센터에서 토큰 재발급")
                print("   - 또는 refresh token으로 자동 갱신")
                
                # Refresh token으로 갱신 시도
                self.try_token_refresh()
                
            elif error['type'] == 'missing_scopes':
                print("\n   [FIX 2] API 권한 추가:")
                print("   1. https://developers.cafe24.com 접속")
                print("   2. 앱 선택 → 권한 설정")
                print("   3. 필요한 권한 체크:")
                for scope in error['scopes']:
                    print(f"      - {scope}")
                print("   4. 저장 후 토큰 재발급")
                
    def try_token_refresh(self):
        """Refresh token으로 토큰 갱신 시도"""
        print("\n   [AUTO] Refresh token으로 자동 갱신 시도...")
        
        # 이 부분은 실제 Cafe24 OAuth refresh 로직 필요
        print("   - oauth_manager.py의 refresh_access_token() 실행")
        print("   - 새 토큰을 Render 환경변수에 업데이트")
        
    def update_render_env(self):
        """Render 환경변수 업데이트 명령 생성"""
        print("\n5. Render 환경변수 업데이트...")
        
        # 새 토큰으로 환경변수 생성
        print("\n   복사할 내용:")
        print("   " + "-" * 40)
        
        # 실제 토큰 데이터 로드
        token_path = r"C:\Users\8899y\Documents\카페24_프로젝트\01_ACTIVE_PROJECT\config\oauth_token.json"
        if os.path.exists(token_path):
            with open(token_path, 'r', encoding='utf-8') as f:
                token_data = json.load(f)
                
            print(f"   CAFE24_ACCESS_TOKEN={token_data.get('access_token', 'NEED_NEW_TOKEN')}")
            print(f"   CAFE24_REFRESH_TOKEN={token_data.get('refresh_token', 'NEED_NEW_TOKEN')}")
            
        print("   " + "-" * 40)
        print("\n   [ACTION] 위 내용을 Render Environment에 업데이트")
        print("   https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg/env")
        
    def run(self):
        """전체 진단 및 수정 실행"""
        # 진단
        self.diagnose_api_errors()
        self.check_token_status()
        
        # 수정
        if self.errors:
            print(f"\n\n[SUMMARY] {len(self.errors)}개 문제 발견")
            self.generate_fixes()
            self.update_render_env()
        else:
            print("\n\n[OK] 문제가 발견되지 않았습니다.")
            
        print("\n" + "=" * 60)
        

def main():
    fixer = APIErrorFixer()
    fixer.run()
    
    print("\n추가 도움:")
    print("1. Cafe24 앱 권한 확인: https://developers.cafe24.com")
    print("2. 새 토큰 발급 후 copy_env_vars.py 실행")
    print("3. GitHub Actions 재실행으로 자동 동기화")


if __name__ == "__main__":
    main()